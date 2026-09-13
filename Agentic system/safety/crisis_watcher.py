"""Runs the crisis verdict and pushes the alert the interface shows.

`crisis_check` returns a structured verdict on the chat participant's newest
messages: explicit self-harm, suicidal intent, or intent to seriously harm
someone else.

`crisis_watch_loop` polls the session for new chat-participant turns and
pushes a `crisis_alert` when the verdict fires. Alerts are throttled, and the
loop sends heartbeats while it waits.

**This is an example, not a safeguarding system.** It shows where a safety
layer attaches to the architecture and what shape its signal takes. It is not
a substitute for a real safeguarding system, and it must not be relied on to
catch every person at risk. A deployment that talks to real chat participants
needs, at least: a validated detection model, human review of every alert, an 
agreed escalation path with someone accountable at the end, current local helpline 
data, and consent from the chat participant and their guardian about what happens 
when the system raises an alert. The interfaces here (the verdict, the `crisis_alert` 
frame, and the cooldown) are the ones the demo pins down; the rest is left to the 
deployment.

Two things worth flagging explicitly for anyone extending this file:
  - `CrisisVerdict.reasons` is prompted to quote the user's own words. That's
    useful for human review, but it means raw self-harm-related text can end
    up in logs, alert payloads, and anything downstream of them. A real
    deployment should decide deliberately who can read that field and for
    how long, not inherit it by default.
  - Both the poll loop and the send helper below swallow their exceptions
    (see the comments at each site). That keeps the demo from crashing on a
    flaky connection, but it also means a missed poll or an undelivered
    alert produces no signal to anyone. A real deployment needs that failure
    to surface somewhere a human will see it.
"""

import asyncio
import json
import time

from pydantic import BaseModel, Field

from config import MODEL_SAFETY
from infrastructure.model_gateway import structured_completion
from prompts import safety as prompts

ALERT_COOLDOWN_S = 30
WATCH_INTERVAL_S = 6

class CrisisVerdict(BaseModel):
    crisis: bool = Field(description="True only for a clear, present risk signal")
    reasons: list[str] = Field(
        default_factory=list,
        description="One short reason per signal, quoting the user's words")

def crisis_check(text: str) -> CrisisVerdict:
    """Judge the newest user text for a clear, present risk signal."""
    return structured_completion(
        MODEL_SAFETY,
        prompts.CRISIS_JUDGE,
        text,
        CrisisVerdict,
        temperature=0.0,
    )

async def crisis_watch_loop(ws, storage, session_id: str) -> None:
    """Poll a session for new user messages and alert the client when risk fires."""
    seen = {"last_ts": 0.0, "last_alert": None}
    while True:
        await asyncio.sleep(WATCH_INTERVAL_S)
        try:
            session = storage.load_session(session_id)
            if not session:
                continue
            fresh = [m for m in session["messages"]
                     if m["role"] == "user" and m["timestamp"] > seen["last_ts"]]
            if not fresh:
                await _send(ws, {"type": "heartbeat", "ts": time.time()})
                continue
                
            # Cap at the last 5 turns so a burst of messages between polls
            # gets judged together instead of one at a time; this is a batching
            # choice, and isn't meant to bound how much history the judge model can see.
            fresh = sorted(fresh, key=lambda m: m["timestamp"])[-5:]
            seen["last_ts"] = fresh[-1]["timestamp"]

            verdict = await asyncio.to_thread(
                crisis_check, "\n---\n".join(m["content"] for m in fresh))
            if not verdict.crisis:
                continue

            now = time.time()
            if seen["last_alert"] and now - seen["last_alert"] < ALERT_COOLDOWN_S:
                continue
            seen["last_alert"] = now
            await _send(ws, {"type": "crisis_alert",
                             "title": prompts.CRISIS_UI_TITLE,
                             "body": prompts.CRISIS_UI_BODY,
                             "payload": verdict.model_dump()})
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            # Swallowed on purpose so one bad poll doesn't kill the loop —
            # but that also means this cycle's messages go unjudged with no
            # record beyond this log line. A production watcher should
            # count/alert on repeated failures.
            print(f"[safety] watch poll failed: {exc}")

async def _send(ws, payload: dict) -> None:
    """Best-effort push to the client socket.

    Exceptions are swallowed deliberately so a closed or flaky socket can't
    take down the watch loop above. The cost is that a dropped `crisis_alert`
    is indistinguishable from a delivered one from here. A real deployment needs a
    delivery guarantee (retry, ack, or a fallback channel) for this specific
    payload type.
    """
    try:
        await ws.send_text(json.dumps(payload))
    except Exception:
        pass
