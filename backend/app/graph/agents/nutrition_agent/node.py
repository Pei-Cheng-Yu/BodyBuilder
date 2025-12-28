from app.graph.state import GraphState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Send

from .prompt import NUTRITION_PROMPT


async def distribute_nutrition(state: GraphState):
    print("Start Distribute Exercise Generation")
    weekly_plan = state["weekly_plan"].schedule
    safety_constraints = state["doctor_suggestion"].safety_constraints
    user_goal = state["profile"].user_goal
    tasks = []
    for daily_plan in weekly_plan:
        if daily_plan.exercises:
            # 1. Construct the message context for THIS specific day
            context_message = HumanMessage(
                content=f"""
                Please give a nutrition hint according my exercise plan:
                - EXERCISE PLAN: {daily_plan.exercises}
                User goal: {user_goal} (might be None)
                """
            )

            # 2. Send to Subgraph
            tasks.append(
                Send(
                    "curator_worker",
                    {
                        "messages": [
                            SystemMessage(content=NUTRITION_PROMPT),
                            context_message,
                        ],
                        "daily_plan": daily_plan,
                        "safety_constraints": safety_constraints,
                    },
                )
            )
    return tasks
