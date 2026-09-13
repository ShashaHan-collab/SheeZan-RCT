"""Delivers tailored advice to the chat participant at the appropriate stage.

The personalization engine writes the plan; this module only decides when the
chat participant should see it. The plan is ready for:

  - a returning chat participant, once the dialogue monitor has cleared them, or
  - a first-time chat participant, once they have kept talking long enough
    after seeing their risk-assessment output (the "snapshot")."""

from config import POST_REPORT_ADVICE_TURNS
from infrastructure.message_protocol import append, event, has_event
from prompts import dialogue_orchestrator as prompts

def _turns_since_snapshot(session: dict) -> int:
    count, seen = 0, False
    for m in session["messages"]:
        if m["role"] == "assistant" and has_event([m], "snapshot"):
            seen = True
            continue
        if seen and m["role"] == "user" and m.get("command") != "get_analysis":
            count += 1
    return count

def offer_advice(session: dict, storage, force: bool = False) -> dict | None:
    if session["state"]["advice_offered"]:
        return None
    if not force and _turns_since_snapshot(session) < POST_REPORT_ADVICE_TURNS:
        return None

    session["state"]["advice_offered"] = True
    reply = prompts.ADVICE_OFFER
    events = [event("get_advice")]
    append(session, "assistant", reply, events=events)
    storage.save_session(session)
    return {"kind": "direct", "reply": reply, "events": events, "done": False}
