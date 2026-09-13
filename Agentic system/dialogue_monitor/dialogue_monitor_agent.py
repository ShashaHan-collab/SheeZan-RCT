"""Monitors the conversation and triggers an assessment based on its evaluation of the dialogue.

`monitor_dialogue` and `judge_readiness` each makes astructured call over the 
message history alone.
 -`monitor_dialogue` checks whether the conversation has covered every dimension
in `dimensions.DIMENSIONS`. The orchestrator uses the summary it returns to
steer the next reply and unlocks the snapshot based on its verdict.

 -`judge_readiness` handles the returning chat participant, whose dimension
check is already done, and gates that session instead. 

 - Neither function writes to the session; state stays with the orchestrator."""

from pydantic import BaseModel, Field

from config import MODEL_MONITOR
from dialogue_monitor.dimensions import DIMENSIONS, coverage_schema
from infrastructure.model_gateway import structured_completion
from prompts import dialogue_monitor as prompts

class ReadinessVerdict(BaseModel):
    ready: bool = Field(description="true = move to the next step, false = keep chatting")

def _chat_text(chat: list[dict]) -> str:
    return "\n".join(
        f"{m['role']}: {m['content']}"
        for m in chat if m.get("role") in ("user", "assistant")
    )

def check_coverage(chat: list[dict], dimensions: list[str]) -> list[str]:
    """Check whether everything still outstanding has been covered."""
    listed = "\n".join(f"- {name}: {DIMENSIONS.get(name, name)}"
                       for name in dimensions)
    verdict = structured_completion(
        MODEL_MONITOR,
        f"{prompts.DIALOGUE_COVERAGE_JUDGE}\n\nSigns:\n{listed}",
        f"Conversation:\n{_chat_text(chat)}",
        coverage_schema(dimensions),
        temperature=0.0,
    )
    return [name for name, value in verdict.model_dump().items() if value == "covered"]

def monitor_dialogue(chat: list, raw_dimensions: list) -> tuple[bool, str, list[str]]:
    found = check_coverage(chat, raw_dimensions)
    missing = [name for name in raw_dimensions if name not in found]
    summary = ", ".join(DIMENSIONS.get(name, name) for name in missing)
    return (not missing), summary, missing

def judge_readiness(chat: list) -> bool:
    verdict = structured_completion(
        MODEL_MONITOR,
        prompts.TRAINING_READINESS_JUDGE,
        f"Conversation:\n{_chat_text(chat)}",
        ReadinessVerdict,
        temperature=0.0,
    )
    return verdict.ready
