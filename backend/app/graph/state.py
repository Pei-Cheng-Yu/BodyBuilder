from typing import TypedDict, List, Optional, Annotated, Union
from app.graph.schema import UserProfile, SegmentalAnalysis
from langgraph.graph import MessagesState

class GraphState(MessagesState):
    inbody_pdf_input: Union[str, bytes]
    profile: Optional[UserProfile]