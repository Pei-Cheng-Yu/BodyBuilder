from app.graph.state import GraphState
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from .node import plan_reconstruct_node, strategy_scheduler_node


def build_strategy_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node(
        "strategy_scheduler",
        strategy_scheduler_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0),
    )
    workflow.add_node("plan_reconstruct", plan_reconstruct_node)

    workflow.add_edge(START, "strategy_scheduler")
    workflow.add_edge("strategy_scheduler", "plan_reconstruct")
    workflow.add_edge("plan_reconstruct", END)

    return workflow.compile()
