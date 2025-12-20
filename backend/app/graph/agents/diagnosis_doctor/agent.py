from app.graph.state import GraphState
from langgraph.graph import END, START, StateGraph

from .node import conlude_suggestion_node, get_weak_part_node


def build_doctor_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("get_weak_part", get_weak_part_node)
    workflow.add_node("conclude_suggestion", conlude_suggestion_node)

    workflow.add_edge(START, "get_weak_part")
    workflow.add_edge("get_weak_part", "conclude_suggestion")
    workflow.add_edge("conclude_suggestion", END)

    return workflow.compile()
