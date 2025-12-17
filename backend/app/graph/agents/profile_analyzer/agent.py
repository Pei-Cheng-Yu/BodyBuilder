from app.graph.state import GraphState
from langgraph.graph import END, START, StateGraph

from .node import inbody_analysis_node


def build_profile_graph():

    workflow = StateGraph(GraphState)
    workflow.add_node("inbody_analysis", inbody_analysis_node)
    workflow.add_edge(START, "inbody_analysis")
    workflow.add_edge("inbody_analysis", END)

    return workflow.compile()
