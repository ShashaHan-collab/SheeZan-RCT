import json
import os
import random
import re
import time
from typing import Optional

from filelock import FileLock

_ID_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

_ID_RE = re.compile(r"^[A-Z0-9]{5,20}$")

def _random_id(length: int) -> str:
    return "".join(random.choice(_ID_ALPHABET) for _ in range(length))

def _valid_id(value: str) -> bool:
    return bool(_ID_RE.fullmatch(value or ""))

class Storage:
    def __init__(self, data_dir: str = "data"):
        self.users_dir = os.path.join(data_dir, "users")
        self.sessions_dir = os.path.join(data_dir, "sessions")
        self.memories_dir = os.path.join(data_dir, "memories")
        self.uids_dir = os.path.join(data_dir, "uids")
        for path in (self.users_dir, self.sessions_dir,
                     self.memories_dir, self.uids_dir):
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def _read(path: str) -> Optional[dict]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    @staticmethod
    def _write(path: str, doc: dict) -> None:
        tmp = path + ".tmp"
        with FileLock(path + ".lock", timeout=10):
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)

    def _fresh_path(self, directory: str, length: int, suffix: str) -> str:
        while True:
            name = _random_id(length)
            path = os.path.join(directory, f"{name}{suffix}.json")
            if not os.path.exists(path):
                return path

    def create_user_id(self) -> str:
        return os.path.basename(self._fresh_path(self.users_dir, 12, "")).split(".")[0]

    def save_user(self, user: dict) -> None:
        if not _valid_id(user.get("user_id", "")):
            raise ValueError("invalid user id")
        self._write(os.path.join(self.users_dir, f"{user['user_id']}.json"), user)

    def load_user(self, user_id: str) -> Optional[dict]:
        if not _valid_id(user_id):
            return None
        return self._read(os.path.join(self.users_dir, f"{user_id}.json"))

    def create_session_id(self) -> str:
        return os.path.basename(self._fresh_path(self.sessions_dir, 8, "")).split(".")[0]

    def save_session(self, session: dict) -> None:
        if not _valid_id(session.get("session_id", "")):
            raise ValueError("invalid session id")
        self._write(
            os.path.join(self.sessions_dir, f"{session['session_id']}.json"), session
        )

    def load_session(self, session_id: str) -> Optional[dict]:
        if not _valid_id(session_id):
            return None
        return self._read(os.path.join(self.sessions_dir, f"{session_id}.json"))

    def create_code_for(self, user_id: str, length: int = 5) -> str:
        """A short, unique public code mapping to the internal user id."""
        path = self._fresh_path(self.uids_dir, length, "")
        code = os.path.basename(path).split(".")[0]
        self._write(path, {"user_id": user_id})
        return code

    def find_user_by_code(self, code: str) -> Optional[str]:
        if not _valid_id(code):
            return None
        doc = self._read(os.path.join(self.uids_dir, f"{code.upper()}.json"))
        return doc["user_id"] if doc else None

    def find_code_for(self, user_id: str) -> Optional[str]:
        for name in os.listdir(self.uids_dir):
            if not name.endswith(".json"):
                continue
            doc = self._read(os.path.join(self.uids_dir, name))
            if doc and doc.get("user_id") == user_id:
                return name[:-5]
        return None

    def save_memory(self, session_id: str, digest: dict) -> None:
        digest["session_id"] = session_id
        digest.setdefault("created_at", time.time())
        self._write(os.path.join(self.memories_dir, f"{session_id}.json"), digest)

    def load_memory(self, session_id: str) -> Optional[dict]:
        if not _valid_id(session_id):
            return None
        return self._read(os.path.join(self.memories_dir, f"{session_id}.json"))
