import time

CHAT_ROLES = ("system", "user", "assistant")

def now() -> float:
    return time.time()

def msg(role: str, content: str, **extra) -> dict:
    return {"role": role, "content": content, "timestamp": now(), **extra}

def append(session: dict, role: str, content: str, events: list | None = None,
           **extra) -> None:
    session["messages"].append(msg(role, content, events=events, **extra))

def event(type_: str, **payload) -> dict:
    return {"type": type_, **payload}

def model_view(session: dict, extra_system: list[str] | None = None) -> list[dict]:
    views = []
    for prompt in extra_system or []:
        views.append({"role": "system", "content": prompt})
    for m in session["messages"]:
        if m["role"] in CHAT_ROLES or m["role"] == "background":
            role = "user" if m["role"] == "background" else m["role"]
            views.append({"role": role, "content": m["content"]})
    return views

def visible_history(session: dict) -> list[dict]:
    return [
        {"role": m["role"], "content": m["content"], "events": m.get("events") or []}
        for m in session["messages"]
        if m["role"] in ("user", "assistant")
    ]

def has_event(messages: list[dict], type_: str) -> bool:
    return any(
        isinstance(e, dict) and e.get("type") == type_
        for m in messages
        for e in m.get("events") or []
    )

def count_user_turns(session: dict) -> int:
    return sum(1 for m in session["messages"] if m["role"] == "user")

def latest_role(session: dict, role: str) -> dict | None:
    for m in reversed(session["messages"]):
        if m["role"] == role:
            return m
    return None
