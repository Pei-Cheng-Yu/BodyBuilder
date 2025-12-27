import operator
import uuid
from typing import Annotated, List, Optional, Union

from app.graph.schema import DailyWorkout, DoctorSuggestion, UserProfile, WeeklyPlan
from langgraph.graph import MessagesState


class GraphState(MessagesState):
    user_id: uuid.UUID
    inbody_pdf_input: Union[str, bytes]
    profile: Optional[UserProfile]
    doctor_suggestion: Optional[DoctorSuggestion]
    weekly_plan: Optional[WeeklyPlan]
    curated_results: Annotated[List[DailyWorkout], operator.add]

    is_dirty: Optional[bool]
    needs_strategy: bool = False
    regen_days: Optional[list[str]] = None
    onboarding_required: bool = False
