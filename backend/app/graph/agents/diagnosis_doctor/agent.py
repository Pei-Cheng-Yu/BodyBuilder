from app.graph.state import GraphState
from langgraph.graph import END, START, StateGraph

from .node import announce_doctor_node, conlude_suggestion_node


def build_doctor_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("announce_doctor", announce_doctor_node)
    workflow.add_node("conclude_suggestion", conlude_suggestion_node)

    workflow.add_edge(START, "announce_doctor")
    workflow.add_edge("announce_doctor", "conclude_suggestion")
    workflow.add_edge("conclude_suggestion", END)

    return workflow.compile()
