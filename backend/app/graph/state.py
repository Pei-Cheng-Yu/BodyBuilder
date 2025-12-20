import operator
from typing import Annotated, List, Optional, Union

from app.graph.schema import DailyWorkout, DoctorSuggestion, UserProfile, WeeklyPlan
from langgraph.graph import MessagesState


class GraphState(MessagesState):
    inbody_pdf_input: Union[str, bytes]
    profile: Optional[UserProfile]
    doctor_suggestion: Optional[DoctorSuggestion]
    weekly_plan: Optional[WeeklyPlan]
    curated_results: Annotated[List[DailyWorkout], operator.add]
