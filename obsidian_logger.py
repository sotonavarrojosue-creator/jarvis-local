import json
from datetime import datetime
from core.config import OBSIDIAN_DIR, OBSIDIAN_LOG_DIR, USER_NAME


def _ensure_dirs():
    OBSIDIAN_LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_to_vault(entry_type: str, message: str, extra: dict | None = None) -> str:
    _ensure_dirs()

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    log_file = OBSIDIAN_LOG_DIR / f"jarvis_{date_str}.md"

    entry = {
        "type": entry_type,
        "user": USER_NAME,
        "time": time_str,
        "message": message,
    }
    if extra:
        entry["extra"] = extra

    header = False
    if not log_file.exists():
        header = True

    with log_file.open("a", encoding="utf-8") as f:
        if header:
            f.write(f"# JARVIS Log — {date_str}\n\n")
            f.write(f"**Usuario:** {USER_NAME}\n\n---\n\n")

        type_emoji = {
            "chat": "💬",
            "skill": "⚡",
            "error": "❌",
            "system": "🔧",
            "reminder": "🔔",
            "voice": "🎤",
        }.get(entry_type, "📝")

        f.write(f"### {type_emoji} [{time_str}] {entry_type.upper()}\n\n")
        f.write(f"{message}\n\n")

        if extra:
            for k, v in extra.items():
                f.write(f"- **{k}**: {v}\n")
            f.write("\n")

        f.write("---\n\n")

    return str(log_file)


def log_chat(user_msg: str, jarvis_response: str) -> str:
    _ensure_dirs()

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    log_file = OBSIDIAN_LOG_DIR / f"jarvis_{date_str}.md"

    header = False
    if not log_file.exists():
        header = True

    with log_file.open("a", encoding="utf-8") as f:
        if header:
            f.write(f"# JARVIS Log — {date_str}\n\n")
            f.write(f"**Usuario:** {USER_NAME}\n\n---\n\n")

        f.write(f"### 💬 [{time_str}] CHAT\n\n")
        f.write(f"**{USER_NAME}:** {user_msg}\n\n")
        f.write(f"**JARVIS:** {jarvis_response}\n\n")
        f.write("---\n\n")

    return str(log_file)


def log_skill(skill_name: str, user_input: str, result: str) -> str:
    return log_to_vault(
        "skill",
        f"Skill **{skill_name}** ejecutado para: *{user_input}*\n\n**Resultado:** {result}",
        extra={"skill": skill_name, "input": user_input},
    )


def log_error(error_msg: str) -> str:
    return log_to_vault("error", error_msg)
