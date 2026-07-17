import json
from datetime import datetime
from core.config import MEMORY_DIR, MAX_MEMORY_MESSAGES

MEMORY_DIR.mkdir(parents=True, exist_ok=True)

__all__ = [
    "load_memory", "save_memory", "clear_memory",
    "list_sessions", "delete_session", "rename_session",
]

_current_session: str = datetime.now().strftime("%Y%m%d")

def _session_file(session_id: str = "") -> str:
    if not session_id:
        session_id = _current_session
    return MEMORY_DIR / f"session_{session_id}.json"

def load_memory(session_id: str = "") -> list:
    f = _session_file(session_id)
    if f.exists():
        try:
            with f.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_memory(messages: list, session_id: str = "") -> None:
    f = _session_file(session_id)
    with f.open("w", encoding="utf-8") as fh:
        json.dump(messages[-MAX_MEMORY_MESSAGES:], fh, ensure_ascii=False, indent=2)

def clear_memory(session_id: str = ""):
    f = _session_file(session_id)
    if f.exists():
        f.unlink()

def list_sessions() -> list[str]:
    return sorted(
        f.stem.replace("session_", "")
        for f in MEMORY_DIR.glob("session_*.json")
    )

def delete_session(session_id: str) -> bool:
    f = MEMORY_DIR / f"session_{session_id}.json"
    if f.exists():
        f.unlink()
        return True
    return False

def rename_session(old_id: str, new_id: str) -> bool:
    old = MEMORY_DIR / f"session_{old_id}.json"
    new = MEMORY_DIR / f"session_{new_id}.json"
    if old.exists():
        old.rename(new)
        return True
    return False
