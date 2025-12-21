from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# --- Global Memory (Simple List) ---
# Note: Data will vanish when the server restarts.
CHAT_HISTORY: List[Dict[str, str]] = []


# --- User Request Schema ---
class ChatRequest(BaseModel):
    message: str


# --- Response Schema ---
class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # 1. Store User Message
    CHAT_HISTORY.append({"role": "user", "content": request.message})

    # 2. Generate Reply (Mock Logic for now)
    reply_text = (
        f"Backend Received: {request.message} (History Size: {len(CHAT_HISTORY)})"
    )

    # 3. Store Assistant Message
    CHAT_HISTORY.append({"role": "assistant", "content": reply_text})

    return ChatResponse(reply=reply_text)
