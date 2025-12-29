import asyncio
import json
import uuid
from typing import Optional

from app.auth.protected import get_current_user
from app.db.models.user import User
from app.graph.agents.consultant.agent import build_consultant_graph
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage

router = APIRouter()


def pick_first(d: dict, key: str):
    """Find the first occurrence of key in a 1-level nested dict structure."""
    if key in d:
        return d[key]
    for v in d.values():
        if isinstance(v, dict) and key in v:
            return v[key]
    return None


def find_last_ai_message(obj):
    """
    Find the last AIMessage in a nested structure (dict/list).
    Returns AIMessage | None
    """
    last = None

    if isinstance(obj, AIMessage):
        return obj

    if isinstance(obj, dict):
        for v in obj.values():
            got = find_last_ai_message(v)
            if got is not None:
                last = got

    elif isinstance(obj, list):
        for item in obj:
            got = find_last_ai_message(item)
            if got is not None:
                last = got

    return last


def ai_content_to_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # list of parts: [{"type":"text","text":"..."}]
        out = []
        for p in content:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict) and p.get("type") == "text":
                out.append(p.get("text", ""))
        return "".join(out).strip()
    if isinstance(content, dict):
        if isinstance(content.get("text"), str):
            return content["text"]
        return json.dumps(content, ensure_ascii=False)
    return str(content)


@router.get("/chat/stream")
async def chat_stream(
    message: str,
    thread_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):

    graph = build_consultant_graph()
    config_thread_id = thread_id or str(uuid.uuid4())
    user_id = current_user.id

    async def event_generator():
        try:
            # 1️⃣ Start
            yield f"data: {json.dumps({'type': 'start', 'thread_id': config_thread_id})}\n\n"

            async for update in graph.astream(
                {
                    "user_id": user_id,
                    "messages": [{"role": "user", "content": message}],
                },
                config={"configurable": {"thread_id": config_thread_id}},
                stream_mode="updates",
            ):
                if isinstance(update, tuple) and len(update) == 2:
                    _, patch = update
                else:
                    patch = update
                system_feedback = pick_first(patch, "system_feedback")
                conclusion_msg = pick_first(patch, "conclusion_msg")

                if system_feedback:
                    yield f"data: {json.dumps({'type':'progress','message':system_feedback}, ensure_ascii=False)}\n\n"
                    continue

                if conclusion_msg:
                    text = ai_content_to_text(conclusion_msg.content)
                    yield f"data: {json.dumps({'type':'message','content':text}, ensure_ascii=False)}\n\n"

        except (GeneratorExit, asyncio.CancelledError):
            return
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        finally:
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
