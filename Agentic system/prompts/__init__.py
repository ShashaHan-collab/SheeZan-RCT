"""
- shared                 profile rendering, time stamp, communication rules
- dialogue_orchestrator  personas, prologues, stage-transition lines
- dialogue_monitor       coverage and readiness verdicts, steering notes
- risk_assessment        snapshot of the current state, domain explainers
- personalization_engine action plan, training choice, memory digest
- coping_skills_training the two guided trainings
- safety                 crisis check and the message it raises"""

from prompts.coping_skills_training import (
    COGNITIVE_RESTRUCTURING_OVERVIEW,
    COGNITIVE_RESTRUCTURING_PHASE1,
    COGNITIVE_RESTRUCTURING_PHASE2,
    COGNITIVE_RESTRUCTURING_REFLECTION,
    MODULE_FINISH_TEXT,
    EPISODIC_FUTURE_THINKING_OVERVIEW,
    EPISODIC_FUTURE_THINKING_PHASE1,
    EPISODIC_FUTURE_THINKING_PHASE2,
    EPISODIC_FUTURE_THINKING_PHASE3,
    EPISODIC_FUTURE_THINKING_PHASE3_POST,
    RATING_ASK,
    RATING_SCALE,
    timeout_rating_question,
    training_background,
)
from prompts.dialogue_monitor import (
    DIALOGUE_COVERAGE_JUDGE,
    STEER_NOTE,
    SYSTEM_NOTE_FORCED,
    SYSTEM_NOTE_JUDGE_NOT_READY,
    SYSTEM_NOTE_JUDGE_READY,
    SYSTEM_NOTE_READY,
    TRAINING_READINESS_JUDGE,
)
from prompts.dialogue_orchestrator import (
    ADVICE_OFFER,
    EPILOGUE_AGREE,
    EPILOGUE_DECLINE,
    FIRST_PROLOGUE,
    REPORT_OFFER,
    RETURN_AGAIN,
    RETURN_DAYS,
    RETURN_HOURS,
    SESSION_DONE_REPLY,
    TRAIN_ASK,
    TRAIN_DECLINE,
    VOICE_GREETING_CONTINUE,
    new_user_persona,
    returning_user_persona,
)
from prompts.personalization_engine import (
    ADVICE_SYSTEM,
    MEMORY_SUMMARISER_SYSTEM,
    TRAINING_CHOICE_JUDGE,
)
from prompts.risk_assessment import (
    DOMAIN_ANALYSIS_FALLBACK,
    DOMAIN_ANALYSIS_SYSTEM,
    SNAPSHOT_SENTENCE,
    SNAPSHOT_SYSTEM,
)
from prompts.safety import (
    CRISIS_JUDGE,
    CRISIS_UI_BODY,
    CRISIS_UI_TITLE,
    SIMULATION_BREAK_SAFETY,
)
from prompts.shared import COMMUNICATION_RULES, now_line, render_profile

__all__ = [
    "ADVICE_OFFER", "ADVICE_SYSTEM", "COMMUNICATION_RULES",
    "COGNITIVE_RESTRUCTURING_OVERVIEW", "COGNITIVE_RESTRUCTURING_PHASE1",
    "COGNITIVE_RESTRUCTURING_PHASE2", "COGNITIVE_RESTRUCTURING_REFLECTION",
    "CRISIS_JUDGE", "CRISIS_UI_BODY", "CRISIS_UI_TITLE",
    "DIALOGUE_COVERAGE_JUDGE", "DOMAIN_ANALYSIS_FALLBACK",
    "DOMAIN_ANALYSIS_SYSTEM", "EPILOGUE_AGREE", "EPILOGUE_DECLINE",
    "FIRST_PROLOGUE", "MEMORY_SUMMARISER_SYSTEM", "MODULE_FINISH_TEXT",
    "EPISODIC_FUTURE_THINKING_OVERVIEW", "EPISODIC_FUTURE_THINKING_PHASE1",
    "EPISODIC_FUTURE_THINKING_PHASE2", "EPISODIC_FUTURE_THINKING_PHASE3",
    "EPISODIC_FUTURE_THINKING_PHASE3_POST", "RATING_ASK", "RATING_SCALE",
    "REPORT_OFFER", "RETURN_AGAIN", "RETURN_DAYS", "RETURN_HOURS",
    "SESSION_DONE_REPLY", "SIMULATION_BREAK_SAFETY", "SNAPSHOT_SENTENCE",
    "SNAPSHOT_SYSTEM", "STEER_NOTE", "SYSTEM_NOTE_FORCED",
    "SYSTEM_NOTE_JUDGE_NOT_READY", "SYSTEM_NOTE_JUDGE_READY",
    "SYSTEM_NOTE_READY", "TRAINING_CHOICE_JUDGE", "TRAINING_READINESS_JUDGE",
    "TRAIN_ASK", "TRAIN_DECLINE", "VOICE_GREETING_CONTINUE",
    "new_user_persona", "now_line", "render_profile", "returning_user_persona",
    "timeout_rating_question", "training_background",
]
