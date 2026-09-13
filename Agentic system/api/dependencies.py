import json
import logging

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from config import data_dir
from infrastructure.message_protocol import has_event
from infrastructure.session_store import Storage
from personalization_engine.user_profile import create_session_memory

logger = logging.getLogger("api")

storage = Storage(data_dir)

def sse(frame: dict) -> str:
    return f"data: {json.dumps(frame, ensure_ascii=False)}\n\n"

def single_event(content: str, done: bool = True, error: bool = False):
    async def generate():
        yield sse({"content": content, "done": done, "error": error})
    return StreamingResponse(generate(), media_type="text/event-stream")

def load_user(user_id: str) -> dict:
    user = storage.load_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

def load_session(session_id: str) -> dict:
    session = storage.load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session

def is_finished(session: dict) -> bool:
    return has_event(session["messages"], "wait_for_checkin")

def archive_finished(user: dict, session: dict) -> None:
    fresh = storage.load_user(user["user_id"])
    for key in ("finished_sessions", "active_session_id",
                "trained_modules", "memories"):
        if fresh and fresh.get(key) is not None:
            user[key] = fresh[key]

    session_id = session["session_id"]
    if session_id not in user.get("finished_sessions", []):
        user.setdefault("finished_sessions", []).append(session_id)
    if user.get("active_session_id") == session_id:
        user["active_session_id"] = None
    storage.save_user(user)

    try:
        create_session_memory(session, storage)
    except Exception as exc:
        logger.warning("memory digest failed for %s: %s", session_id, exc)
