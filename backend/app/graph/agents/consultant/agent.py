from app.graph.agents.consultant.node import (
    announce_curator,
    announce_strategy,
    conclusion_node,
    consultant_node,
    load_user_context_node,
    route_after_doctor,
    route_after_profile,
    route_after_tasks,
    route_delegate,
    run_tasks_node,
    sync_db_node,
)
from app.graph.agents.diagnosis_doctor.agent import build_doctor_graph
from app.graph.agents.exercise_curator.agent import build_curator_graph
from app.graph.agents.profile_analyzer.agent import build_profile_graph
from app.graph.agents.strategy_planner.agent import build_strategy_graph
from app.graph.state import GraphState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph


def build_consultant_graph():
    doctor_agent = build_doctor_graph()
    curator_agent = build_curator_graph()
    strategy_agent = build_strategy_graph()
    profile_agent = build_profile_graph()

    workflow = StateGraph(GraphState)
    workflow.add_node("load_user_context", load_user_context_node)
    workflow.add_node("consultant", consultant_node)
    workflow.add_node("run_tasks", run_tasks_node)
    workflow.add_node("sync_db", sync_db_node)

    workflow.add_node("profile_agent", profile_agent)
    workflow.add_node("doctor_agent", doctor_agent)
    workflow.add_node("strategy_agent", strategy_agent)
    workflow.add_node("curator_agent", curator_agent)
    workflow.add_node("conclusion", conclusion_node)
    workflow.add_node("announce_curator", announce_curator)
    workflow.add_node("announce_strategy", announce_strategy)

    workflow.add_edge("announce_curator", "curator_agent")
    workflow.add_edge("announce_strategy", "strategy_agent")
    workflow.add_edge(START, "load_user_context")
    workflow.add_edge(
        "load_user_context",
        "consultant",
    )

    workflow.add_conditional_edges(
        "consultant",
        route_delegate,
        {
            "__end__": "conclusion",
            "run_tasks": "run_tasks",
        },
    )
    workflow.add_conditional_edges(
        "profile_agent",
        route_after_profile,
        {
            "doctor": "doctor_agent",
            "sync_db": "sync_db",
        },
    )
    workflow.add_conditional_edges(
        "run_tasks",
        route_after_tasks,
        {
            "update_inbody": "profile_agent",
            "doctor": "doctor_agent",
            "sync_db": "sync_db",
            "__end__": "conclusion",
        },
    )
    workflow.add_conditional_edges(
        "doctor_agent",
        route_after_doctor,
        {
            "strategy": "announce_strategy",
            "curator": "announce_curator",
            "sync_db": "sync_db",
        },
    )
    workflow.add_edge("strategy_agent", "announce_curator")
    workflow.add_edge("curator_agent", "sync_db")
    workflow.add_edge("sync_db", "conclusion")
    workflow.add_edge("conclusion", END)
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
