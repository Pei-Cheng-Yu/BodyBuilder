from app.graph.state import GraphState
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .node import (
    CuratorState,
    announce_curator,
    curator_agent,
    distribute_exercise,
    formalizer_node,
    plan_compiler_node,
)
from .tool import search_exercise_tool


def build_curator_agent():
    builder = StateGraph(CuratorState, output_schema=GraphState)
    builder.add_node("agent", curator_agent)
    builder.add_node("tools", ToolNode([search_exercise_tool]))
    builder.add_node("formalizer", formalizer_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "formalizer",  # When no more tool calls, go to formalizer
        },
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("formalizer", END)
    return builder.compile()


def build_curator_graph():
    curator_worker = build_curator_agent()

    workflow = StateGraph(GraphState)
    workflow.add_node("announce_curator", announce_curator)
    workflow.add_node("curator_worker", curator_worker)
    workflow.add_node("plan_compiler", plan_compiler_node)

    workflow.add_edge(START, "announce_curator")
    workflow.add_conditional_edges(
        "announce_curator", distribute_exercise, {"curator_worker": "curator_worker"}
    )

    workflow.add_edge("curator_worker", "plan_compiler")
    workflow.add_edge("plan_compiler", END)

    return workflow.compile()
