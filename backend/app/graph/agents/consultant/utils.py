import json

from app.graph.state import GraphState
from langchain_core.messages import HumanMessage, ToolMessage


def last_human_text(state: GraphState) -> str:
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            return m.content  # "I want to set my goal to lose 10kg and workout 4x/week"
    return ""


def should_regen_exercises(state: GraphState) -> bool:
    if state.get("regen_days"):
        return True
    plan = state.get("weekly_plan")
    return bool(
        plan
        and any(d.need_exercise_generate and not d.is_rest_day for d in plan.schedule)
    )


def make_tool_ack(tool_call_id: str, tasks: list[str]):
    return ToolMessage(
        tool_call_id=tool_call_id,
        content=json.dumps({"ok": True, "tasks": tasks}),
    )


def make_tool_error(tool_call_id: str, code: str, message: str, tasks: list[str]):
    return ToolMessage(
        tool_call_id=tool_call_id,
        content=json.dumps(
            {
                "ok": False,
                "tasks": tasks,
                "error": {"code": code, "message": message},
            }
        ),
    )
