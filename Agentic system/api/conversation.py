import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dialogue_orchestrator.dialogue_orchestrator import (
    DialogueOrchestrator,
    stream_llm_reply,
)
from infrastructure.concurrency_locks import session_lock
from personalization_engine.advice_agent import stream_advice, stored_advice
from prompts import dialogue_orchestrator as prompts
from risk_assessment.risk_assessment_agent import assess_risk
from api.dependencies import (
    archive_finished,
    is_finished,
    load_session,
    load_user,
    sse,
    single_event,
    storage,
)

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    query: str
    command: str | None = None
    module: str | None = None

class FinishRequest(BaseModel):
    session_id: str
    query: str = ""

@router.post("/api/chat")
async def chat(req: ChatRequest):
    lock = session_lock(req.session_id)
    await lock.acquire()
    try:
        session = load_session(req.session_id)
        user = load_user(session["user_id"])

        if is_finished(session):
            lock.release()
            return single_event(prompts.SESSION_DONE_REPLY)

        orchestrator = DialogueOrchestrator(session, user, storage)
        action = await asyncio.to_thread(
            orchestrator.handle_turn, req.query, "text", req.command, req.module,
        )

        if action["kind"] == "direct":
            lock.release()
            return single_event(action["reply"])

        storage.save_session(session)
        async def stream():
            try:
                async for chunk in stream_llm_reply(session, storage):
                    yield sse(chunk)
            finally:
                lock.release()

        return StreamingResponse(stream(), media_type="text/event-stream")
    except BaseException:
        if lock.locked():
            lock.release()
        raise

@router.post("/api/get_snapshot")
async def get_snapshot(req: ChatRequest):
    session = load_session(req.session_id)
    load_user(session["user_id"])
    try:
        return single_event(assess_risk(session, storage))
    except Exception as exc:
        print(f"[api] snapshot failed: {exc}")
        raise HTTPException(502, "The snapshot could not be written right now")

@router.post("/api/get_advice")
async def get_advice(req: ChatRequest):
    session = load_session(req.session_id)
    load_user(session["user_id"])
    if session["state"].get("advice_done"):
        return single_event(stored_advice(session) or "")

    async def stream():
        async for chunk in stream_advice(session, storage):
            yield sse(chunk)

    return StreamingResponse(stream(), media_type="text/event-stream")

@router.post("/api/finish")
async def finish(req: FinishRequest):
    lock = session_lock(req.session_id)
    await lock.acquire()
    try:
        session = load_session(req.session_id)
        user = load_user(session["user_id"])
        if session["session_id"] in user.get("finished_sessions", []):
            raise HTTPException(400, "This session is already finished")

        agreed = req.query.strip().lower() in (
            "yes", "sure", "ok", "okay", "agree", "yep", "true", "1")
        archive_finished(user, session)
        return {
            "epilogue": (prompts.EPILOGUE_AGREE if agreed
                         else prompts.EPILOGUE_DECLINE),
            "memory": storage.load_memory(session["session_id"]) or {},
        }
    finally:
        lock.release()
