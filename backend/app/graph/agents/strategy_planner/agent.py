from app.graph.state import GraphState
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from .node import announce_strategy, plan_reconstruct_node, strategy_scheduler_node


def build_strategy_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node(
        "strategy_scheduler",
        strategy_scheduler_node,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0),
    )
    workflow.add_node("plan_reconstruct", plan_reconstruct_node)
    workflow.add_node("announce_strategy", announce_strategy)

    workflow.add_edge(START, "announce_strategy")
    workflow.add_edge("announce_strategy", "strategy_scheduler")
    workflow.add_edge("strategy_scheduler", "plan_reconstruct")
    workflow.add_edge("plan_reconstruct", END)

    return workflow.compile()
