import time

from personalization_engine.context_retriever import days_since
from prompts import dialogue_orchestrator as prompts

def _memory_text(digest: dict) -> str:
    fields = (
        ("About them", digest.get("profile_notes", "")),
        ("How they are now", digest.get("current_state", "")),
        ("What matters to them", " / ".join(digest.get("concerns", []))),
        ("Agreed plan to follow up", digest.get("agreed_plan", "")),
        ("Their strengths", digest.get("strengths", "")),
        ("Recent events", " / ".join(digest.get("important_events", []))),
    )
    return "".join(f"- {label}: {value}\n" for label, value in fields if value)

def build_persona(user: dict, context: dict) -> str:
    digest = context.get("digest")
    if not digest:
        return prompts.new_user_persona(user["profile"])
    return prompts.returning_user_persona(
        user["profile"],
        session_count=context["session_count"],
        days_since_last=days_since(digest.get("created_at") or time.time()),
        memory_digest=_memory_text(digest) or "(no memories recorded)",
        pending_plan=digest.get("agreed_plan", ""),
    )
