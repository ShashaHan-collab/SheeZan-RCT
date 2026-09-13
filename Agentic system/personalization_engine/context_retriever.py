import math
import time

def days_since(timestamp: float) -> int:
    return max(0, math.floor((time.time() - timestamp) / 86400))

def retrieve_context(user: dict, storage) -> dict:
    finished = user.get("finished_sessions", [])
    digest = storage.load_memory(finished[-1]) if finished else None
    return {
        "session_count": len(finished),
        "digest": digest,
        "last_finished_at": (digest or {}).get("created_at"),
    }
