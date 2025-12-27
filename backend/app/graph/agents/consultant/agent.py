from app.graph.agents.consultant.node import (
    consultant_node,
    load_user_context_node,
    route_after_doctor,
    route_after_profile,
    route_after_tasks,
    route_delegate,
    route_trigger_generate,
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


def build_auto_planning_graph():
    workflow = StateGraph(GraphState)

    curator_agent = build_curator_graph()
    strategy_agent = build_strategy_graph()

    workflow.add_node("strategy_agent", strategy_agent)
    workflow.add_node("curator_agent", curator_agent)

    workflow.add_edge(START, "strategy_agent")
    workflow.add_edge("strategy_agent", "curator_agent")
    workflow.add_edge("curator_agent", END)
    return workflow.compile()


def build_consultant_graph():
    doctor_agent = build_doctor_graph()
    curator_agent = build_curator_graph()
    strategy_agent = build_strategy_graph()
    profile_agent = build_profile_graph()
    auto_planning = build_auto_planning_graph()
    workflow = StateGraph(GraphState)
    workflow.add_node("load_user_context", load_user_context_node)
    workflow.add_node("consultant", consultant_node)
    workflow.add_node("run_tasks", run_tasks_node)
    workflow.add_node("sync_db", sync_db_node)

    workflow.add_node("profile_agent", profile_agent)
    workflow.add_node("doctor_agent", doctor_agent)
    workflow.add_node("strategy_agent", strategy_agent)
    workflow.add_node("curator_agent", curator_agent)
    workflow.add_node("auto_planning", auto_planning)

    workflow.add_edge(START, "load_user_context")
    workflow.add_conditional_edges(
        "load_user_context",
        route_trigger_generate,
        {"auto_planning": "auto_planning", "consultant_node": "consultant"},
    )
    workflow.add_edge("auto_planning", "sync_db")
    workflow.add_conditional_edges(
        "consultant",
        route_delegate,
        {"__end__": END, "update_inbody": "profile_agent", "run_tasks": "run_tasks"},
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
        {"doctor": "doctor_agent", "sync_db": "sync_db", "__end__": END},
    )
    workflow.add_conditional_edges(
        "doctor_agent",
        route_after_doctor,
        {
            "strategy": "strategy_agent",
            "curator": "curator_agent",
            "sync_db": "sync_db",
        },
    )
    workflow.add_edge("strategy_agent", "curator_agent")
    workflow.add_edge("curator_agent", "sync_db")
    workflow.add_edge("sync_db", END)
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
