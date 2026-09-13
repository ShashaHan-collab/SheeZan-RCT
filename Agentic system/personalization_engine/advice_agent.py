from config import MODEL_ADVICE
from infrastructure.message_protocol import append, event, latest_role
from infrastructure.model_gateway import stream_chat
from prompts import personalization_engine as prompts
from prompts.shared import render_profile
from risk_assessment.risk_assessment_agent import SNAPSHOT_RECORD

def _conversation_text(session: dict) -> str:
    return "\n".join(
        f"{m['role']}: {m['content']}"
        for m in session["messages"]
        if m["role"] in ("user", "assistant")
    )

def stored_advice(session: dict) -> str | None:
    for m in reversed(session["messages"]):
        if m["role"] == "assistant" and any(
            e.get("type") == "advice" for e in (m.get("events") or [])
        ):
            return m["content"]
    return None

def stream_advice(session: dict, storage):
    user = storage.load_user(session["user_id"])
    snapshot = latest_role(session, SNAPSHOT_RECORD)
    full = ""

    async def generate():
        nonlocal full
        try:
            async for delta in stream_chat(
                MODEL_ADVICE,
                [
                    {"role": "system", "content": prompts.ADVICE_SYSTEM},
                    {"role": "user",
                     "content": (
                         f"Conversation:\n{_conversation_text(session)}\n\n"
                         f"Snapshot of the current state:\n"
                         f"{snapshot['content'] if snapshot else '(none)'}\n\n"
                         f"Profile:\n{render_profile(user['profile'])}"
                     )},
                ],
                temperature=0.2,
            ):
                full += delta
                yield {"content": delta, "done": False}
            append(session, "assistant", full, events=[event("advice")])
            session["state"]["advice_done"] = True
            storage.save_session(session)
            yield {"content": "", "done": True}
        except Exception as exc:
            yield {"content": f"Sorry, I stumbled there: {exc}", "done": True,
                   "error": True}

    return generate()
