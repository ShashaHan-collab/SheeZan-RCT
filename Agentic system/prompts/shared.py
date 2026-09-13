"""
Example prompt templates in English.

These prompts illustrate the agent roles in SheeZan. They are provided for
reviewer evaluation and are not direct translations of the production prompts,
which were written in Chinese and codesigned with stakeholders as described in
the Article.

The full production prompt set may include additional local contextual
elements and safety constraints.

"""
from datetime import datetime
from zoneinfo import ZoneInfo

_PROFILE_LABELS = {
    "age": "Age",
    "gender": "Gender",
    "education": "Education stage",
    "background": "Hometown city level",
    "live": "Living arrangement",
    "live_with": "Mainly lives with",
    "use_phone_time": "Daily phone time (last week)",
    "social_behavior": "Social-media habits (last week)",
    "interests": "Hobbies and interests",
}

def render_profile(profile: dict) -> str:
    lines = []
    for key, label in _PROFILE_LABELS.items():
        value = profile.get(key)
        if isinstance(value, list):
            value = ", ".join(value)
        if value not in (None, ""):
            lines.append(f"- {label}: {value}")
    return "\n".join(lines)

def now_line() -> str:
    """Gives the assistant the current date and time, so "the past two weeks"
        and "this week" point at real dates."""
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    return now.strftime("The current date and time is %Y-%m-%d %H:%M (%A).")

COMMUNICATION_RULES = """Communication rules (non-negotiable):
- Never use clinical or screening terminology such as "mental health", "symptom", "disorder", "diagnosis", or "risk" in anything you say to the user. Talk like a caring friend, not a clinician.
- Never ask more than one question in a single reply.
- When the user shows strong emotion, acknowledge and sit with it first; never jump straight into problem-solving.
- Never lecture. Avoid "you should...", "why don't you just..." phrasing; offer possibilities instead.
- Never invent personal experiences. It is fine to say "some people find that..." but never "back when I was your age...".
- Keep every reply short, natural, spoken-style sentences; at most a short paragraph unless the current stage requires a structured deliverable (snapshot, action plan, training steps).
- If the user expresses anything that sounds like they may hurt themselves or others, pause whatever you are doing, respond with immediate warmth and concern, and encourage them to reach a trusted adult or a professional right now. Never debate, minimise, or leave them alone with the topic.
- Never end the conversation on your own initiative; always hand the next move to the user."""
