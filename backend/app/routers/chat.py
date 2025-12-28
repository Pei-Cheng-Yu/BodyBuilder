from typing import Dict, List

from app.auth.protected import get_current_user
from app.db.models.user import User
from fastapi import APIRouter, Depends
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
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    CHAT_HISTORY.append(
        {
            "role": "user",
            "user_id": str(current_user.id),
            "content": request.message,
        }
    )

    # 2. Generate Reply
    reply_text = (
        f"User {current_user.email}: {request.message} "
        f"(History Size: {len(CHAT_HISTORY)})"
    )

    # 3. Store Assistant Message
    CHAT_HISTORY.append(
        {
            "role": "assistant",
            "content": reply_text,
        }
    )
    return ChatResponse(reply=reply_text)
