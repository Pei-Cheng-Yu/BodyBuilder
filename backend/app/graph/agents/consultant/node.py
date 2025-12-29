from typing import Literal

from app.db.models import MedicalPrescription as SQLMedical
from app.db.models import User
from app.db.models import UserProfile as SQLProfile
from app.db.models import WeeklyPlan as SQLWeeklyPlan
from app.db.session import AsyncSessionLocal
from app.graph.llm.gemini import get_gemini
from app.graph.llm.ollama import get_ollama_gpt_120
from app.graph.schema import DoctorSuggestion, UserProfile, WeeklyPlan
from app.graph.state import GraphState
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from .prompt import CONCLUSION_INSTRUCTION, MODEL_SYSTEM_MESSAGE
from .tool import update_plan, update_profile
from .utils import (
    extract_ai_text,
    last_human_text,
    make_tool_ack,
    make_tool_error,
    should_regen_exercises,
)


class DelegateTask(BaseModel):
    tasks: list[Literal["user", "plan_changing", "inbody"]]
    days: list[str] = []
    instruction: str | None = None


# === node ====


async def load_user_context_node(state: GraphState):
    feedback = "👤 Gather and analyzing your profile and preferences…"
    user_id = state["user_id"]

    async with AsyncSessionLocal() as session:
        # Fetch the User with Profile, Medical, and current Plan in ONE query
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.prescription),
                selectinload(User.weekly_plans),
            )
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        return {"onboarding_required": True}

    # This "dumps" the DB data into your schema and calculates FFMI/TDEE
    profile_data = None
    if user.profile is not None:
        profile_data = UserProfile.model_validate(user.profile)

    prescription = user.prescription  # may be None
    doctor_suggestion = None

    if prescription is not None:
        doctor_suggestion = DoctorSuggestion.model_validate(
            prescription, from_attributes=True
        )
    active_plan = None
    if user.weekly_plans:
        sql_plan = user.weekly_plans[-1]
        active_plan = WeeklyPlan.model_validate(sql_plan.plan_data)
    # Do the same for Medical and WeeklyPlan if you have schemas for them

    latest_scan = None
    if profile_data is not None:
        latest_scan = profile_data.latest_scan

    return {
        "profile": profile_data,
        "doctor_suggestion": doctor_suggestion,
        "weekly_plan": active_plan,
        "onboarding_required": latest_scan is None,
        "system_feedback": feedback,
    }


async def consultant_node(state: GraphState):
    user_profile = state.get("profile")
    week_plan = state.get("weekly_plan")
    doctor_suggestion = state.get("doctor_suggestion")
    onboarding_required = state.get("onboarding_required")
    system_msg = MODEL_SYSTEM_MESSAGE.format(
        user_profile=user_profile,
        doctor_suggestion=doctor_suggestion,
        weekly_plan=week_plan,
        onboarding_required=onboarding_required,
    )
    llm = get_gemini().bind_tools([DelegateTask])
    user_msg = state["messages"][-1]
    resp = await llm.ainvoke([SystemMessage(system_msg), user_msg])

    return {"messages": [resp], "consultant_msg": resp}


def route_delegate(
    state: GraphState,
) -> Literal["__end__", "run_tasks", "update_inbody"]:
    msg = state["messages"][-1]
    if not getattr(msg, "tool_calls", None):
        return "__end__"

    tasks = msg.tool_calls[0]["args"]["tasks"]

    # inbody often implies full recompute, handle separately if you want
    if "inbody" in tasks:
        return "update_inbody"
    return "run_tasks"


async def run_tasks_node(state: GraphState):
    msg = state["messages"][-1]
    tool_call = msg.tool_calls[0]
    tasks = tool_call["args"]["tasks"]

    if isinstance(tasks, str):
        tasks = [tasks]

    # Guard: plan_changing requires weekly_plan
    if "plan_changing" in tasks and not state.get("weekly_plan"):
        err = make_tool_error(
            tool_call_id=tool_call["id"],
            code="NO_WEEKLY_PLAN",
            message="No weekly plan exists yet. Generate a weekly plan first.",
            tasks=tasks,
        )
        return {"messages": [err], "is_dirty": False}

    ack = make_tool_ack(tool_call_id=tool_call["id"], tasks=tasks)

    # Working copy of state
    current = state
    feedback = "🛠 Applying your requested changes…"
    out = {"messages": [ack], "system_feedback": feedback, "actions": []}

    # Profile update first
    if "user" in tasks:
        patch_out = await update_profile(current)
        out.update(patch_out)
        out.setdefault("actions", []).append("updated_profile")
        current = {**current, **patch_out}  # 🔑 THIS IS THE KEY

    # Plan update uses updated profile
    if "plan_changing" in tasks:
        plan_out = await update_plan(current)
        out.update(plan_out)
        out.setdefault("actions", []).append("updated_plan")
        if out.get("regen_days"):
            days = out["regen_days"]
            out["actions"].append(f"regen_exercises for: {days}")
        current = {**current, **plan_out}

    return out


def route_after_profile(state: GraphState):
    profile = state.get("profile")
    has_scan = bool(profile and getattr(profile, "latest_scan", None))
    if has_scan:
        return "doctor"
    return "sync_db"


def route_after_tasks(state: GraphState):
    if not state.get("is_dirty"):
        return "__end__"

    profile = state.get("profile")
    has_scan = bool(profile and getattr(profile, "latest_scan", None))

    if has_scan:
        return "doctor"
    return "sync_db"


def route_after_doctor(state: GraphState) -> Literal["strategy", "curator", "sync_db"]:
    profile = state.get("profile")
    has_scan = bool(profile and getattr(profile, "latest_scan", None))
    has_weekly_plan = bool(state.get("weekly_plan"))

    if has_scan and not has_weekly_plan:
        return "strategy"
    elif state.get("needs_strategy", False):
        return "strategy"
    elif should_regen_exercises(state):
        return "curator"
    else:
        return "sync_db"


async def sync_db_node(state: GraphState):
    """
    The Single Source of Truth Persistor.
    Takes Pydantic snapshots from state and 'dumps' them into Postgres.
    """
    feedback = "✅ All set! Everything is Saved to your profile"
    if not state.get("is_dirty"):
        return {"is_dirty": False, "system_feedback": "✅ Nothing to save."}

    user_id = state["user_id"]

    async with AsyncSessionLocal() as session:

        # 1. Sync User Profile
        if state.get("profile"):
            # Convert Pydantic -> Dict (mode='json' handles JSONB columns)
            profile_data = state["profile"].model_dump(
                mode="json", exclude_unset=True, exclude_none=True
            )
            profile_data["user_id"] = user_id

            # Use 'Upsert' logic (Insert or Update if exists)
            stmt = insert(SQLProfile).values(**profile_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["user_id"], set_=profile_data
            )
            await session.execute(stmt)

        # 2. Sync Medical Prescription
        if state.get("doctor_suggestion"):
            medical_data = state["doctor_suggestion"].model_dump(
                mode="json", exclude_unset=True, exclude_none=True
            )
            medical_data["user_id"] = user_id

            stmt = insert(SQLMedical).values(**medical_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["user_id"], set_=medical_data
            )
            await session.execute(stmt)

        if state.get("weekly_plan"):
            # deactivate existing active plans for this user
            await session.execute(
                update(SQLWeeklyPlan)
                .where(
                    SQLWeeklyPlan.user_id == user_id, SQLWeeklyPlan.is_active.is_(True)
                )
                .values(is_active=False)
            )

            plan_data = state["weekly_plan"].model_dump(
                mode="json", exclude_unset=True, exclude_none=True
            )

            new_plan = SQLWeeklyPlan(
                user_id=user_id,
                plan_data=plan_data,
                is_active=True,
            )
            session.add(new_plan)

        await session.commit()

    # Reset the flag so we don't save twice
    return {"is_dirty": False, "system_feedback": feedback, "actions": ["saved_to_db"]}


async def conclusion_node(state: GraphState):
    actions = state.get("actions") or []
    feedback = state.get("system_feedback")
    profile = state.get("profile")
    weekly_plan = state.get("weekly_plan")
    doctor = state.get("doctor_suggestion")
    request = last_human_text(state)
    ai_msg = state.get("consultant_msg")
    text = extract_ai_text(ai_msg)
    message = CONCLUSION_INSTRUCTION.format(
        ai_msg=text,
        feedback=feedback,
        user_request=request,
        profile=profile,
        weekly_plan=weekly_plan,
        actions=actions,
        doctor_suggestion=doctor,
    )

    llm = get_ollama_gpt_120()
    response = await llm.ainvoke(message)

    return {"conclusion_msg": response}
