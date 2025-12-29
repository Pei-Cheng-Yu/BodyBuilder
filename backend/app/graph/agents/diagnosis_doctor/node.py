from typing import Optional

from app.graph.llm.ollama import get_ollama
from app.graph.schema import DoctorSuggestion
from app.graph.state import GraphState
from pydantic import BaseModel, Field

from .prompt import DIAGNOSIS_PROMPT
from .utils import identify_weak_parts


class DiagnosisNote(BaseModel):
    user_goal: Optional[str]
    weak_parts: Optional[list[str]] = Field(
        None, description="user's weak body part that need to have more training"
    )


class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")


def announce_doctor_node(state: GraphState):
    feedback = "🩺 Quick safety check — reviewing health constraints…"
    print("⚡ Running Weak Part Diagnosis...")

    return {
        "system_feedback": feedback,
    }


# def get_progress_node


async def conlude_suggestion_node(state: GraphState):
    seg = state["profile"].latest_scan.segmental_muscle
    weak_parts = identify_weak_parts(seg)
    user_goal = state["profile"].user_goal
    injuries = state["profile"].injuries
    llm = get_ollama()

    prompt = DIAGNOSIS_PROMPT.format(
        weak_parts=weak_parts,
        goal=user_goal,
        injuries=injuries,
    )

    structured_llm = llm.with_structured_output(DoctorSuggestion)

    doctor_suggetsion = await structured_llm.ainvoke(prompt)
    return {"doctor_suggestion": doctor_suggetsion, "is_dirty": True}
