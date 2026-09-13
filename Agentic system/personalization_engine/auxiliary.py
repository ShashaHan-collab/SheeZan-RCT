from typing import Literal

from pydantic import BaseModel, Field

from config import MODEL_ADVICE
from infrastructure.message_protocol import model_view
from infrastructure.model_gateway import structured_completion
from prompts import personalization_engine as prompts

BALANCE_LOW = 0.4
BALANCE_HIGH = 2.5

class TrainingChoice(BaseModel):
    training: Literal["Cognitive_Restructuring", "Episodic_Future_Thinking"]
    reason: str = Field(description="One sentence, for the project log")

def _balance(choice: str, history: list[str]) -> str:
    cognitive = history.count("Cognitive_Restructuring")
    future = history.count("Episodic_Future_Thinking")
    if not cognitive and not future:
        return choice
    ratio = cognitive / future if future else float("inf")
    if BALANCE_LOW <= ratio <= BALANCE_HIGH:
        return choice
    return "Cognitive_Restructuring" if cognitive < future else "Episodic_Future_Thinking"

def recommend_training(session: dict, user: dict) -> str:
    history = user.get("trained_modules", []) or []
    chat = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in model_view(session) if m["role"] in ("user", "assistant")
    )
    choice = structured_completion(
        MODEL_ADVICE,
        prompts.TRAINING_CHOICE_JUDGE,
        f"Conversation so far:\n{chat}\n\n"
        f"Trainings already completed by this user: {history or 'none'}",
        TrainingChoice,
        temperature=0.0,
    )
    return _balance(choice.training, history)
