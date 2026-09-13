"""The training agents. They activate based on chat history and past training performance.

Both trainings run through the same three phases:

    phase 1   name the material: the thought that got stuck, or the situation
              the chat participant keeps putting off (model-led; closes with
              the 1–10 rating question)
    phase 2   do the work: test the thought and rebalance it, or play the
              unchanged future forward (model-led; closes with the rating
              question again)
    phase 3   close it out: a short scripted closing — one question for
              Cognitive Restructuring, two for Episodic Future Thinking

`PHASE_GUIDANCE` below is the model-led half; `PHASE_3_SCRIPT` is the scripted
half.

The rating question drives the transitions: the model asks it at the end of
phases 1 and 2, the chat participant answers with a number, and the agent
advances to the next phase. If a phase runs long without the chat participant
answering, the agent asks the rating question itself (see `PHASE_CAP`).
"""

import re

from coping_skills_training.training_interaction import PHASE_CAP, RATING_MARKERS
from infrastructure.message_protocol import append, event, latest_role
from prompts import coping_skills_training as prompts

PHASE_1, PHASE_2, PHASE_3 = "1", "2", "3"
NUMBER_RE = re.compile(r"^\s*\d{1,2}\s*$")
PHASE_GUIDANCE = {
    ("Cognitive_Restructuring", PHASE_1): prompts.COGNITIVE_RESTRUCTURING_PHASE1,
    ("Cognitive_Restructuring", PHASE_2): prompts.COGNITIVE_RESTRUCTURING_PHASE2,
    ("Episodic_Future_Thinking", PHASE_1): prompts.EPISODIC_FUTURE_THINKING_PHASE1,
    ("Episodic_Future_Thinking", PHASE_2): prompts.EPISODIC_FUTURE_THINKING_PHASE2,
}

PHASE_3_SCRIPT = {
    "Cognitive_Restructuring": [
        (prompts.COGNITIVE_RESTRUCTURING_REFLECTION, "cognitive_select"),
    ],
    "Episodic_Future_Thinking": [
        (prompts.EPISODIC_FUTURE_THINKING_PHASE3, None),
        (prompts.EPISODIC_FUTURE_THINKING_PHASE3_POST, None),
    ],
}

# Phase flow: start_training -> phase 1 -rating-> phase 2 -rating-> phase 3 -> done
#
# Phases 1 and 2 are model-led (prompts from PHASE_GUIDANCE). Phase 3 is
# scripted (lines from PHASE_3_SCRIPT, one per turn). Every chat-participant
# turn enters through module_turn; a phase transition can only happen there.

def start_training(session: dict, storage) -> dict:
    state = session["state"]
    state["phase"] = PHASE_1
    user = storage.load_user(session["user_id"])
    append(session, "system", _overview_prompt(state["module"]))
    append(session, "system", _phase_prompt(state["module"], PHASE_1))
    append(session, "background", _background(session, user))
    storage.save_session(session)
    return {"kind": "stream"}

def module_turn(session: dict, storage, query: str) -> dict:
    state = session["state"]
    module = state["module"]
    phase = state["phase"]

    if phase in (PHASE_1, PHASE_2):
        if _rating_answered(session, phase, query):
            return _enter_next_phase(session, storage)
    else:
        return _phase_3_turn(session, storage, module)

    if len(_region(session)) - _phase_start_offset(session) >= PHASE_CAP:
        reply = _timeout_question(module, phase)
        append(session, "assistant", reply)
        storage.save_session(session)
        return {"kind": "direct", "reply": reply, "done": False}

    return {"kind": "stream"}

def _rating_answered(session: dict, phase: str, query: str) -> bool:
    """True when the user just answered this phase's closing rating."""
    asked = sum(1 for m in _region(session)
                if m["role"] == "assistant" and _is_rating_ask(m["content"]))
    return _is_rating_answer(query) and asked >= int(phase)

def _enter_next_phase(session: dict, storage) -> dict:
    state = session["state"]
    module = state["module"]

    if state["phase"] == PHASE_1:
        state["phase"] = PHASE_2
        append(session, "system", _phase_prompt(module, PHASE_2))
        storage.save_session(session)
        return {"kind": "stream"}

    state["phase"] = PHASE_3
    state["step"] = 0
    storage.save_session(session)
    return _phase_3_turn(session, storage, module)

def _phase_3_turn(session: dict, storage, module: str) -> dict:
    state = session["state"]
    script = PHASE_3_SCRIPT[module]
    step = state.get("step", 0)

    if step >= len(script):
        _close_training(session, storage)
        last = latest_role(session, "assistant")
        return {"kind": "direct", "reply": last["content"], "done": True}

    line, signal = script[step]
    state["step"] = step + 1
    events = [event(signal)] if signal else []
    append(session, "assistant", line, events=events)
    storage.save_session(session)
    return {"kind": "direct", "reply": line, "events": events, "done": False}

def _close_training(session: dict, storage) -> None:
    state = session["state"]
    state["train_done"] = True
    state["phase"] = "done"
    append(session, "training_tip", "finished")

    user = storage.load_user(session["user_id"])
    user.setdefault("trained_modules", []).append(state["module"])
    storage.save_user(user)

    reply = prompts.MODULE_FINISH_TEXT[state["module"]]
    append(session, "assistant", reply, events=[event("wait_for_checkin")])
    storage.save_session(session)


def _region(session: dict) -> list:
    out, collecting = [], False
    for m in session["messages"]:
        if m["role"] == "select_train":
            collecting = True
            continue
        if collecting:
            out.append(m)
    return out

def _phase_start_offset(session: dict) -> int:
    return sum(1 for m in _region(session) if m["role"] == "system")

def _is_rating_answer(text: str) -> bool:
    if NUMBER_RE.match(text) and 0 < int(text) <= 10:
        return True
    return text.strip().lower() in (
        "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine", "ten",
    )

def _is_rating_ask(content: str) -> bool:
    lowered = content.lower()
    return any(marker in lowered for marker in RATING_MARKERS)

def _overview_prompt(module: str) -> str:
    return {
        "Cognitive_Restructuring": prompts.COGNITIVE_RESTRUCTURING_OVERVIEW,
        "Episodic_Future_Thinking": prompts.EPISODIC_FUTURE_THINKING_OVERVIEW,
    }[module]

def _phase_prompt(module: str, phase: str) -> str:
    return PHASE_GUIDANCE[(module, phase)]

def _timeout_question(module: str, phase: str) -> str:
    return prompts.timeout_rating_question(module, phase)

def _advice_text(session: dict) -> str | None:
    for m in reversed(session["messages"]):
        if m["role"] == "assistant" and any(
            e.get("type") == "advice" for e in (m.get("events") or [])
        ):
            return m["content"]
    return None

def _background(session: dict, user: dict) -> str:
    parts = []
    snapshot = latest_role(session, "snapshot_content")
    if snapshot:
        parts.append("Snapshot written about this user earlier:\n" + snapshot["content"])

    advice = _advice_text(session)
    if advice:
        parts.append("Action plan just given:\n" + advice[:600])

    recent = [m for m in session["messages"] if m["role"] in ("user", "assistant")][-6:]
    if recent:
        lines = "\n".join(f"{m['role']}: {m['content'][:300]}" for m in recent)
        parts.append("Latest exchanges:\n" + lines)
    return prompts.training_background("\n\n".join(parts), user["profile"])
