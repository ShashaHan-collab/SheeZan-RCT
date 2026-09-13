import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from dialogue_orchestrator.dialogue_orchestrator import init_session
from infrastructure.concurrency_locks import session_lock, user_lock
from infrastructure.message_protocol import visible_history
from api.dependencies import (
    archive_finished,
    is_finished,
    load_session,
    load_user,
    storage,
)

router = APIRouter()

"""These profile fields are for demo purposes only and do not represent the data required in production."""
class Profile(BaseModel):
    age: int
    gender: str
    education: str
    background: str
    live: str
    live_with: str
    use_phone_time: str
    social_behavior: str
    interests: list[str] = Field(default_factory=list)

class RegisterRequest(BaseModel):
    profile: Profile

class LoginRequest(BaseModel):
    code: str

class SessionRequest(BaseModel):
    user_id: str

class SessionIdRequest(BaseModel):
    session_id: str

@router.post("/api/register")
async def register(req: RegisterRequest):
    user_id = storage.create_user_id()
    code = storage.create_code_for(user_id)
    user = {
        "user_id": user_id,
        "code": code,
        "profile": req.profile.model_dump(),
        "created_at": time.time(),
        "active_session_id": None,
        "finished_sessions": [],
        "trained_modules": [],
        "memories": [],
    }
    storage.save_user(user)
    return {"user_id": user_id, "code": code}

@router.post("/api/login")
async def login(req: LoginRequest):
    user_id = storage.find_user_by_code(req.code)
    user = storage.load_user(user_id) if user_id else None
    if not user:
        raise HTTPException(404, "Unknown code — please check and try again")
    return {"user_id": user["user_id"], "code": user["code"]}

@router.post("/api/overview")
async def overview(req: SessionRequest):
    user = load_user(req.user_id)

    sessions = []
    for session_id in reversed(user.get("finished_sessions", [])):
        memory = storage.load_memory(session_id) or {}
        sessions.append({
            "session_id": session_id,
            "finished_at": memory.get("created_at"),
            "module": memory.get("module"),
            "preview": memory.get("current_state", "")[:240],
            "digest": memory,
        })

    active = None
    if user.get("active_session_id"):
        session = storage.load_session(user["active_session_id"])
        if session:
            finished = is_finished(session)
            active = {
                "session_id": session["session_id"],
                "created_at": session["created_at"],
                "finished": finished,
                "messages": visible_history(session)[-4:],
            }
            if finished:
                lock = session_lock(session["session_id"])
                await lock.acquire()
                try:
                    archive_finished(load_user(req.user_id), session)
                finally:
                    lock.release()

    return {
        "user_id": user["user_id"],
        "code": user["code"],
        "created_at": user["created_at"],
        "trained_modules": user.get("trained_modules", []),
        "active_session": active,
        "sessions": sessions,
    }

@router.post("/api/create_session")
async def create_session(req: SessionRequest):
    lock = user_lock(req.user_id)
    await lock.acquire()
    try:
        user = load_user(req.user_id)

        if user.get("active_session_id"):
            session = storage.load_session(user["active_session_id"])
            if session:
                if not is_finished(session):
                    return {"session_id": session["session_id"],
                            "messages": visible_history(session)}
                archive_finished(user, session)

        session = init_session(storage, user)
        storage.save_session(session)
        user["active_session_id"] = session["session_id"]
        storage.save_user(user)
        return {"session_id": session["session_id"],
                "prologue": visible_history(session)[-1]["content"]}
    finally:
        lock.release()

@router.post("/api/get_session")
async def get_session(req: SessionIdRequest):
    return {"messages": visible_history(load_session(req.session_id))}
