from pydantic import BaseModel, Field

from config import MODEL_ADVICE
from infrastructure.model_gateway import structured_completion
from prompts import personalization_engine as prompts

class SessionMemory(BaseModel):
    profile_notes: str = Field(description="Who the user is and their situation, in their own words")
    current_state: str = Field(description="How the user is feeling now and what matters most to them")
    concerns: list[str] = Field(default_factory=list, description="One line per concern voiced")
    strengths: str = Field(description="The user's own resilience signals and who supports them")
    agreed_plan: str = Field(description="What was suggested and whether the user agreed")
    closing_mood: str = Field(description="Mood and engagement at the end of the session")
    important_events: list[str] = Field(default_factory=list, description="Significant events the user shared")

def create_session_memory(session: dict, storage) -> dict:
    transcript = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in session["messages"]
        if m["role"] in ("user", "assistant")
    )
    memory: SessionMemory = structured_completion(
        MODEL_ADVICE,
        prompts.MEMORY_SUMMARISER_SYSTEM,
        f"Session transcript:\n{transcript}",
        SessionMemory,
        temperature=0.2,
    )
    digest = memory.model_dump()
    digest["module"] = session["state"].get("module")
    storage.save_memory(session["session_id"], digest)

    user = storage.load_user(session["user_id"])
    user.setdefault("memories", []).append(session["session_id"])
    storage.save_user(user)
    return digest
