from typing import Optional, Union

from app.graph.schema import UserProfile
from langgraph.graph import MessagesState


class GraphState(MessagesState):
    inbody_pdf_input: Union[str, bytes]
    profile: Optional[UserProfile]
