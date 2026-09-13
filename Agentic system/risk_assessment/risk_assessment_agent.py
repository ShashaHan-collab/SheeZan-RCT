"""Conducts health risk assessment across the designated health domains. """

from pydantic import BaseModel, Field

from config import MODEL_ASSESSMENT
from infrastructure.message_protocol import append, event, latest_role
from infrastructure.model_gateway import complete_chat, structured_completion
from prompts import risk_assessment as prompts
from prompts.shared import render_profile


SNAPSHOT_RECORD = "snapshot_content"

class SnapshotReport(BaseModel):
    anxiety_level: str = Field(description="One of: High, Medium-High, Medium, Medium-Low, Low")
    low_mood_level: str = Field(description="One of: High, Medium-High, Medium, Medium-Low, Low")
    anxiety_basis: str = Field(description="1-2 second-person sentences: what the user said that shaped this level")
    low_mood_basis: str = Field(description="1-2 second-person sentences: what the user said that shaped this level")
    school_analysis: str = Field(description="Second-person analysis; 'Not mentioned' if absent")
    family_analysis: str = Field(description="Second-person analysis; 'Not mentioned' if absent")
    peer_analysis: str = Field(description="Second-person analysis; 'Not mentioned' if absent")
    self_analysis: str = Field(description="Second-person analysis; 'Not mentioned' if absent")

def _conversation_text(session: dict) -> str:
    return "\n".join(
        f"{m['role']}: {m['content']}"
        for m in session["messages"]
        if m["role"] in ("user", "assistant")
    )

def _has_snapshot(message: dict) -> bool:
    return any(e.get("type") == "snapshot" for e in (message.get("events") or []))

def assess_risk(session: dict, storage) -> str:
    for m in reversed(session["messages"]):
        if m["role"] == "assistant" and _has_snapshot(m):
            return m["content"]

    user = storage.load_user(session["user_id"])
    report: SnapshotReport = structured_completion(
        MODEL_ASSESSMENT,
        prompts.SNAPSHOT_SYSTEM,
        f"Conversation:\n{_conversation_text(session)}\n\n"
        f"Profile:\n{render_profile(user['profile'])}",
        SnapshotReport,
        temperature=0.2,
    )

    append(session, SNAPSHOT_RECORD,
           f"Anxiety level: {report.anxiety_level}\n"
           f"Low-mood level: {report.low_mood_level}\n"
           f"School: {report.school_analysis}\n"
           f"Family: {report.family_analysis}\n"
           f"Friends: {report.peer_analysis}\n"
           f"Self: {report.self_analysis}")

    visible = (
        "Here is the gentle snapshot I promised.\n\n"
        f"### Anxiety\n{report.anxiety_level} — {report.anxiety_basis}\n\n"
        f"### Low mood\n{report.low_mood_level} — {report.low_mood_basis}\n\n"
        + prompts.SNAPSHOT_SENTENCE
    )
    append(session, "assistant", visible, events=[event("snapshot")])
    storage.save_session(session)
    return visible

def explain_domain(session: dict) -> str:
    record = latest_role(session, SNAPSHOT_RECORD)
    question = ""
    for m in reversed(session["messages"]):
        if m["role"] == "user" and m.get("command") == "get_analysis":
            question = m["content"].strip()
            break
    return complete_chat(
        MODEL_ASSESSMENT,
        [
            {"role": "system", "content": prompts.DOMAIN_ANALYSIS_SYSTEM},
            {"role": "user",
             "content": f"### Snapshot\n{record['content']}\n\n"
                        f"### Question\n{question}"},
        ],
        temperature=0.2,
    )
