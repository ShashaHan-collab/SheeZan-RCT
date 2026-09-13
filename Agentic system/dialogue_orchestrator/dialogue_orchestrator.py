"""Manages the conversation flow and state transitions.

One instance handles one turn. It looks at the session's state, decides what
the companion does next, and returns an action that the API layer turns into
a response:

    {"kind": "stream"}                       the model replies
    {"kind": "direct", "reply", "events"}    the app answers on its own

Main session states: inquiry, risk_communication, advice_communication, training

Text and voice share the same state machine. Voice runs native full-duplex
(simultaneous speaking, listening, and interruption handled by the audio
layer, not here), but once a chat participant's turn is complete it is
routed through `handle_turn` like a text turn, and the reply is spoken back."""

import time

from config import (
    ADVICE_CHECK_START,
    HARD_MAX_TURNS,
    MODEL_DIALOGUE,
    REPORT_CHECK_START,
)
from coping_skills_training.coping_skills_training import module_turn, start_training
from coping_skills_training.training_interaction import TRAINING_MODULES
from dialogue_monitor import dialogue_monitor_agent as monitor
from dialogue_monitor.dimensions import DIMENSIONS, merge_covered, uncovered
from dialogue_orchestrator import advice_communicator
from infrastructure.message_protocol import (
    append,
    count_user_turns,
    event,
    has_event,
    latest_role,
    model_view,
)
from infrastructure.model_gateway import stream_chat
from personalization_engine.auxiliary import recommend_training
from personalization_engine.context_retriever import days_since, retrieve_context
from personalization_engine.dialogue_adaption import build_persona
from prompts import dialogue_monitor as monitor_prompts
from prompts import dialogue_orchestrator as prompts
from risk_assessment.risk_assessment_agent import SNAPSHOT_RECORD, explain_domain

STATE_INQUIRY = "inquiry"
STATE_RISK_COMMUNICATION = "risk_communication"
STATE_ADVICE_COMMUNICATION = "advice_communication"
STATE_TRAINING = "training"
STATE_DONE = "done"


def init_session(storage, user: dict) -> dict:
    context = retrieve_context(user, storage)
    session = {
        "session_id": storage.create_session_id(),
        "user_id": user["user_id"],
        "messages": [],
        "created_at": time.time(),
        "state": {
            "prior_assessment": bool(user.get("finished_sessions")),
            "covered": [],            
            "advice_done": False,     
            "advice_offered": False,  
            "module": None,           
            "phase": None,            
            "step": 0,               
            "train_done": False,
            "skip_offer": False,      
        },
    }
    append(session, "system", build_persona(user, context))
    append(session, "assistant", build_prologue(context["last_finished_at"]))
    return session

def build_prologue(last_finished_at: float | None) -> str:
    if last_finished_at is None:
        return prompts.FIRST_PROLOGUE
    hours = (time.time() - last_finished_at) / 3600
    if hours < 1:
        return prompts.RETURN_AGAIN
    if hours < 24:
        return prompts.RETURN_HOURS
    return prompts.RETURN_DAYS.format(days=days_since(last_finished_at))


class DialogueOrchestrator:

    def __init__(self, session: dict, user: dict, storage):
        self.session = session
        self.user = user
        self.storage = storage
        self.query = ""            
        self.command = None       
        self.module = None

    @property
    def state(self) -> str:
        state = self.session["state"]
        if state.get("train_done") or state.get("skip_offer"):
            return STATE_DONE
        if state.get("module"):
            return STATE_TRAINING
        if state.get("advice_done"):
            return STATE_ADVICE_COMMUNICATION
        if has_event(self.session["messages"], "snapshot"):
            return STATE_RISK_COMMUNICATION
        return STATE_INQUIRY

    def handle_turn(self, query: str, source: str = "text",
                    command: str | None = None,
                    module: str | None = None) -> dict:
        self.query, self.command, self.module = query, command, module
        append(self.session, "user", query, type=source,
               command=command, module=module)


        if command == "get_analysis":
            answer = self._handle_domain_question()
            if answer:
                return answer

        handler = {
            STATE_INQUIRY: self._handle_inquiry,
            STATE_RISK_COMMUNICATION: self._handle_risk_communication,
            STATE_ADVICE_COMMUNICATION: self._handle_advice_communication,
            STATE_TRAINING: self._handle_training,
            STATE_DONE: self._handle_done,
        }[self.state]
        return handler()


    def _handle_inquiry(self) -> dict:
        state = self.session["state"]
        turns = count_user_turns(self.session)

        if state["advice_offered"]:
            return {"kind": "stream"}

        if state["prior_assessment"]:
            due = turns >= ADVICE_CHECK_START and (turns % 2 == 1 or turns > 25)
            if due:
                if monitor.judge_readiness(self._chat()):
                    append(self.session, "judge_agent_tip",
                           monitor_prompts.SYSTEM_NOTE_JUDGE_READY)
                    return advice_communicator.offer_advice(
                        self.session, self.storage, force=True)
                append(self.session, "judge_agent_tip",
                       monitor_prompts.SYSTEM_NOTE_JUDGE_NOT_READY)
                self.storage.save_session(self.session)
            return {"kind": "stream"}

        if turns < REPORT_CHECK_START or turns % 2 == 0:
            return {"kind": "stream"}
        return self._check_coverage()

    def _check_coverage(self) -> dict:
        session = self.session
        missing = uncovered(session)
        found = monitor.check_coverage(self._chat(), missing)
        covered = merge_covered(session, found)
        self.storage.save_session(session)

        forced = count_user_turns(session) >= HARD_MAX_TURNS
        if len(covered) < len(DIMENSIONS) and not forced:
            self._steer_to_gaps(uncovered(session))
            return {"kind": "stream"}
        return self._signal_snapshot(forced)

    def _steer_to_gaps(self, missing: list[str]) -> None:
        """Nudge the persona toward uncovered dimensions.

        The self-harm dimension follows a separate, more conservative rollout
        policy (see config). If it surfaces on its own, the persona's crisis
        rules take over first.
        """
        steerable = [key for key in missing if key != "suicidal_ideation"] 
        if not steerable:
            return
        note = monitor_prompts.STEER_NOTE.format(
            labels=", ".join(DIMENSIONS[key] for key in steerable))
        for m in reversed(self.session["messages"]):
            if m["role"] == "system":
                m["content"] += "\n" + note
                break
        append(self.session, "judge_agent_tip", note)
        self.storage.save_session(self.session)

    def _signal_snapshot(self, forced: bool) -> dict:
        note = (monitor_prompts.SYSTEM_NOTE_FORCED if forced
                else monitor_prompts.SYSTEM_NOTE_READY)
        append(self.session, "judge_agent_tip", "System: " + note)
        reply = prompts.REPORT_OFFER
        events = [event("get_snapshot")]
        append(self.session, "assistant", reply, events=events)
        self.storage.save_session(self.session)
        return {"kind": "direct", "reply": reply, "events": events, "done": False}

    def _handle_domain_question(self) -> dict | None:
        if not latest_role(self.session, SNAPSHOT_RECORD):
            return None
        try:
            reply = explain_domain(self.session)
        except Exception as exc:  
            print(f"[dialogue] domain explainer failed: {exc}")
            reply = prompts.DOMAIN_ANALYSIS_FALLBACK
        append(self.session, "assistant", reply)
        self.storage.save_session(self.session)
        return {"kind": "direct", "reply": reply, "events": [], "done": False}


    def _handle_risk_communication(self) -> dict:
        action = advice_communicator.offer_advice(self.session, self.storage)
        return action or {"kind": "stream"}


    def _handle_advice_communication(self) -> dict:
        state = self.session["state"]

        if self.command == "start_train" and self.module in TRAINING_MODULES:
            state["module"] = self.module
            state["phase"] = None
            append(self.session, "select_train", self.module)
            self.storage.save_session(self.session)
            return start_training(self.session, self.storage)

        if self.command == "offer_train":
            training = recommend_training(self.session, self.user)
            reply = prompts.TRAIN_ASK.format(module=TRAINING_MODULES[training])
            events = [event("ask_train", module=training)]
            append(self.session, "assistant", reply, events=events)
            self.storage.save_session(self.session)
            return {"kind": "direct", "reply": reply, "events": events,
                    "done": False}

        if self.command == "skip_train":
            state["skip_offer"] = True
            reply = prompts.TRAIN_DECLINE
            events = [event("wait_for_checkin")]
            append(self.session, "assistant", reply, events=events)
            self.storage.save_session(self.session)
            return {"kind": "direct", "reply": reply, "events": events, "done": True}

        return {"kind": "stream"}


    def _handle_training(self) -> dict:
        return module_turn(self.session, self.storage, self.query)


    def _handle_done(self) -> dict:
        return {"kind": "direct", "reply": prompts.SESSION_DONE_REPLY,
                "events": [], "done": True}


    def _chat(self) -> list[dict]:
        return [m for m in model_view(self.session)
                if m["role"] in ("user", "assistant")]


def stream_llm_reply(session: dict, storage):
    full = ""

    async def generate():
        nonlocal full
        try:
            async for delta in stream_chat(MODEL_DIALOGUE, model_view(session),
                                           temperature=0.8):
                full += delta
                yield {"content": delta, "done": False}
            append(session, "assistant", full)
            storage.save_session(session)
            yield {"content": "", "done": True}
        except Exception as exc:
            yield {"content": f"Sorry, I stumbled there: {exc}", "done": True,
                   "error": True}

    return generate()
