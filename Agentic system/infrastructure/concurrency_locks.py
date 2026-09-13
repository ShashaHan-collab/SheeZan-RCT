import asyncio

_session_locks: dict[str, asyncio.Lock] = {}
_user_locks: dict[str, asyncio.Lock] = {}

def session_lock(session_id: str) -> asyncio.Lock:
    return _session_locks.setdefault(session_id, asyncio.Lock())

def user_lock(user_id: str) -> asyncio.Lock:
    return _user_locks.setdefault(user_id, asyncio.Lock())
