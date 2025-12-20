from typing import Optional

from app.graph.llm.ollama import get_ollama, get_ollama_gpt_120
from app.graph.schema import DailyWorkout, ExerciseDetail
from app.graph.state import GraphState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState
from langgraph.types import Send
from pydantic import BaseModel, Field

from .prompt import CURATOR_PROMPT
from .tool import search_exercise_tool


class WorkoutFills(BaseModel):
    """Output schema for the Curator Agent."""

    exercises: list[ExerciseDetail] = Field(
        ..., description="The curated list of exercises found."
    )


class CuratorState(MessagesState):
    daily_plan: Optional[DailyWorkout]
    safety_constraints: list[str]


def distribute_exercise(state: GraphState):
    print("Start Distribute Exercise Generation")
    weekly_plan = state["weekly_plan"].schedule
    safety_constraints = state["doctor_suggestion"].safety_constraints

    tasks = []
    for daily_plan in weekly_plan:
        if daily_plan.need_exercise_generate and not daily_plan.is_rest_day:
            # 1. Construct the message context for THIS specific day
            context_message = HumanMessage(
                content=f"""
                Please find exercises for the following workout:
                - FOCUS AREA: {daily_plan.focus_area}
                - COACH INSTRUCTIONS: {daily_plan.coach_instructions}
                - SAFETY CONSTRAINTS: {safety_constraints}
                """
            )

            # 2. Send to Subgraph
            tasks.append(
                Send(
                    "curator_worker",
                    {
                        "messages": [
                            SystemMessage(content=CURATOR_PROMPT),
                            context_message,
                        ],
                        "daily_plan": daily_plan,
                        "safety_constraints": safety_constraints,
                    },
                )
            )
    return tasks


async def curator_agent(state: CuratorState):
    llm = get_ollama_gpt_120().bind_tools([search_exercise_tool])
    # The agent just processes the messages in its private state
    response = await llm.ainvoke(state["messages"])
    if response.tool_calls:
        print(
            f"🎯 Agent decided to call tools: {[t['name'] for t in response.tool_calls]}"
        )
    else:
        print("⚠️ Agent DID NOT call any tools!")
    return {"messages": [response]}


async def formalizer_node(state: CuratorState) -> GraphState:
    """The final step inside the Subgraph"""
    extraction_prompt = SystemMessage(
        content="""
        Review the history, there is a Daily Plan about exercise.
        Based on Daily Plan, output the final exercise list in JSON format
        matching the OUTPUT SCHEMA defined in your instructions.
        Do not call any more tools. Return ONLY the JSON.

        ### OUTPUT SCHEMA
        You must provide the following fields for each exercise:
        - `exercise_id`: (string) The raw ID from the tool.
        - `name`: (string) Full exercise name.
        - `sets`: (integer) Total sets.
        - `reps`: (string) e.g., "8-12".
        - `note`: (string) One safety cue.
        - `steps`: (list of strings) The instructions.
    """
    )
    llm = get_ollama_gpt_120()

    messages = state["messages"][-4:-1] + [extraction_prompt]
    response = await llm.ainvoke(messages)

    gemma = get_ollama()  # Local
    cleaner_llm = gemma.with_structured_output(WorkoutFills)

    fixer_prompt = f"""
    I have exercise search results. Extract them into the 'WorkoutFills' JSON schema.
    Keep the exercise_ids, notes, and steps exactly as they appear in the text.

    RAW TEXT:
    {response}
    """

    fixed_result = await cleaner_llm.ainvoke(fixer_prompt)

    # 3. Update the workout object
    workout = state["daily_plan"]
    workout.exercises = fixed_result.exercises
    workout.need_exercise_generate = False

    return {"curated_results": [workout]}


def plan_compiler_node(state: GraphState):
    print("🧩 Re-assembling the final Weekly Plan...")

    original_schedule = state["weekly_plan"].schedule

    # Get the hydrated days (the results from the parallel Curators)
    # We convert this list to a dictionary for fast lookup: {"Monday": WorkoutObj, ...}
    hydrated_days = {workout.day: workout for workout in state["curated_results"]}

    final_schedule = []

    #  Iterate through the original 7 days and replace where necessary
    for skeleton_day in original_schedule:
        if skeleton_day.day in hydrated_days:
            # We found a match! Use the one with exercises.
            print(f"   ✅ Merging exercises into {skeleton_day.day}")
            final_schedule.append(hydrated_days[skeleton_day.day])
        else:
            # This was likely a rest day or not processed; keep as is.
            final_schedule.append(skeleton_day)

    updated_plan = state["weekly_plan"]
    updated_plan.schedule = final_schedule

    return {"weekly_plan": updated_plan, "curated_results": []}
