from datetime import datetime
from typing import Literal, Optional

from app.graph.llm.ollama import get_ollama_gpt_120
from app.graph.schema import DailyWorkout, UserProfile
from app.graph.state import GraphState
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from trustcall import create_extractor

from .prompt import TRUSTCALL_INSTRUCTION
from .utils import last_human_text


class ProfileChangeRequest(BaseModel):
    user_goal: Optional[str] = None
    workout_frequency: Optional[int] = Field(None, ge=1, le=7)
    injuries: Optional[list[str]] = None
    load: Optional[int] = None

    training_location: Optional[Literal["gym", "home", "both"]] = None
    available_equipment: Optional[list[str]] = None

    avoid_equipment: Optional[list[str]] = None


class DayPlanChange(BaseModel):
    day: str = Field(
        ...,
        description="Target day to modify. Examples: 'Monday', 'Wednesday', 'today', 'Day 3'",
    )
    is_rest_day: Optional[bool] = Field(
        None,
        description="Set true to convert this day to a rest day, false to make it a training day.",
    )
    regenerate_exercises: bool = Field(
        default=False,
        description="If true, regenerate exercises for this day using current constraints.",
    )
    user_instruction: Optional[str] = Field(
        None, description="User requested adjustment for this day only"
    )


class PlanChangeRequest(BaseModel):
    scope: Literal["days", "rebuild_week"] = "days"
    days: list[DayPlanChange] = Field(default_factory=list)


def normalize_day(s: str) -> str:
    return s.strip().lower()


def resolve_day_alias(day: str) -> str:
    if normalize_day(day) == "today":
        return datetime.now().strftime("%A").lower()  # e.g. "sunday"
    return normalize_day(day)


def apply_day_change(daily: DailyWorkout, change: DayPlanChange) -> DailyWorkout:

    update_fields = {}

    if change.is_rest_day is not None:
        update_fields["is_rest_day"] = change.is_rest_day

    if change.user_instruction is not None:
        update_fields["user_instruction"] = change.user_instruction

    updated = daily.model_copy(update=update_fields)

    has_instruction = bool(change.user_instruction and change.user_instruction.strip())

    if updated.is_rest_day:
        updated.exercises = []
        updated.need_exercise_generate = False
    else:
        # ✅ if instruction exists, we also regen
        if change.regenerate_exercises or has_instruction:
            updated.exercises = []
            updated.need_exercise_generate = True

    return updated


async def update_profile(state: GraphState):
    old_profile = state.get("profile")

    llm = get_ollama_gpt_120()
    user_request = last_human_text(state)

    is_new_profile = old_profile is None

    messages = [
        SystemMessage(TRUSTCALL_INSTRUCTION),
        HumanMessage(user_request),  # "set my goal to lose 10kg, workout 4x/week"
    ]

    extractor = create_extractor(
        llm, tools=[ProfileChangeRequest], tool_choice="ProfileChangeRequest"
    )

    result = await extractor.ainvoke({"messages": messages})

    # Extract & apply patch (same as yours)
    patch = next(
        (r for r in result.get("responses", []) if isinstance(r, ProfileChangeRequest)),
        None,
    )

    update_data = patch.model_dump(exclude_none=True)

    if is_new_profile:
        update_data = patch.model_dump(exclude_none=True)
        new_profile = UserProfile(**update_data)  # create from partial fields
    else:
        update_data = patch.model_dump(exclude_none=True)
        new_profile = old_profile.model_copy(update=update_data)

    structural = any(k in update_data for k in ["workout_frequency"])  # injuries too(?)

    return {
        "profile": new_profile,
        "needs_strategy": structural,
        "is_dirty": True,
    }


async def update_plan(state: GraphState):
    weekly_plan = state["weekly_plan"]  # safe because guard handled missing plan

    user_request = last_human_text(state)
    if not user_request:
        # safest is no-op (or set system_feedback if your state has it)
        return {}

    llm = get_ollama_gpt_120()
    extractor = create_extractor(
        llm,
        tools=[PlanChangeRequest],
        tool_choice="PlanChangeRequest",
    )
    result = await extractor.ainvoke(
        {"messages": [SystemMessage(TRUSTCALL_INSTRUCTION), HumanMessage(user_request)]}
    )

    req = next(
        (r for r in result.get("responses", []) if isinstance(r, PlanChangeRequest)),
        None,
    )
    if not req or not req.days:
        # no-op so the graph doesn't crash
        return {}

    changes = {resolve_day_alias(c.day).lower(): c for c in req.days}

    new_schedule = []
    regen_days = []

    for daily in weekly_plan.schedule:
        key = daily.day.lower()
        if key not in changes:
            new_schedule.append(daily)
            continue

        updated = apply_day_change(daily, changes[key])
        if updated.need_exercise_generate:
            regen_days.append(updated.day)
        new_schedule.append(updated)

    new_weekly_plan = weekly_plan.model_copy(update={"schedule": new_schedule})

    return {
        "weekly_plan": new_weekly_plan,
        "regen_days": regen_days or None,
        "is_dirty": True,
    }
