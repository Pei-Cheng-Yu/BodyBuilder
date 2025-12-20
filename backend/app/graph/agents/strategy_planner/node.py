from app.graph.llm.ollama import get_ollama, get_ollama_gpt_20
from app.graph.schema import DailyWorkout, WeeklyPlan
from app.graph.state import GraphState
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from .prompt import STRATEGY_COACH_PROMPT


class DailyNote(BaseModel):
    day: str = Field(..., description="Day of the week (e.g., 'Monday' or 'Day 1')")
    is_rest_day: bool = Field(..., description="True if this is a recovery day")
    focus_area: str = Field(
        ..., description="Target muscles (e.g., 'Legs - Quads focus')"
    )
    coach_instructions: str = Field(
        ...,
        description="Specific directive for this day (e.g., 'Keep intensity high, use drop sets').",
    )


class WeeklyNote(BaseModel):
    plan_name: str = Field(
        ..., description="Name of the split (e.g., 'PPL Hypertrophy Phase')"
    )
    goal_summary: str = Field(
        ..., description="Brief explanation of why this plan fits the user."
    )

    # This list allows us to easily map-reduce later
    schedule: list[DailyNote] = Field(..., description="List of 7 daily plans.")


class TempState(TypedDict):
    unstructured_weekly_plan: WeeklyNote


async def strategy_scheduler_node(state: GraphState) -> TempState:
    print("🧠 Strategy Coach is planning the week...")
    doctor_suggestion = state.get("doctor_suggestion")
    profile = state.get("profile")

    if not doctor_suggestion:
        print("⚠️ No Doctor Prescription found. Using defaults.")
        # Create a dummy object or handle error
        target_focus = []
        constraints = []
        load = "Standard Hypertrophy"
    else:
        target_focus = doctor_suggestion.target_focus_areas
        constraints = doctor_suggestion.safety_constraints
        load = doctor_suggestion.load_recommendation

    freq = profile.workout_frequency
    context_str = f"""
    USER LOGISTICS:
    - Frequency: {freq} days/week
    This means you MUST provide exactly {freq} workout days and {7 - freq} rest days.
    - Goal: {profile.user_goal}

    MEDICAL PRESCRIPTION (FROM DOCTOR):
    - Priority Focus Areas: {target_focus}
    - Safety Constraints: {constraints}
    - Load Guidelines: {load}
    """

    llm = get_ollama_gpt_20()

    structured_llm = llm.with_structured_output(WeeklyNote, method="function_calling")

    result = await structured_llm.ainvoke(
        [
            SystemMessage(content=STRATEGY_COACH_PROMPT),
            SystemMessage(content=context_str),
        ]
    )

    gemma = get_ollama()  # Local
    cleaner_llm = gemma.with_structured_output(WeeklyNote)

    fixer_prompt = f"""
    Extract the following training plan into a valid JSON object.
    KEEP the logic, instructions, and focus areas identical.
    ENSURE every day (Monday-Sunday) is present in the 'schedule' list.
    ALL the DATA should be same, dont change the data value
    Include the `is_rest_day`
    DATA TO FIX:
    {result}
    """

    fixed_result = await cleaner_llm.ainvoke(fixer_prompt)
    return {"unstructured_weekly_plan": fixed_result}


def plan_reconstruct_node(state: TempState) -> GraphState:
    uncontructed_plan = state["unstructured_weekly_plan"]

    contructed_schedule = []

    for daily_note in uncontructed_plan.schedule:
        daily_workout = DailyWorkout(
            day=daily_note.day,
            is_rest_day=daily_note.is_rest_day,
            focus_area=daily_note.focus_area,
            coach_instructions=daily_note.coach_instructions,
            need_exercise_generate=True,
            exercises=[],  # <--- empty list for the Curator later
        )
        contructed_schedule.append(daily_workout)

    final_plan = WeeklyPlan(
        plan_name=uncontructed_plan.plan_name,
        goal_summary=uncontructed_plan.goal_summary,
        schedule=contructed_schedule,
    )
    print(f"✅ Plan Created: {final_plan.plan_name}")
    return {"weekly_plan": final_plan}
