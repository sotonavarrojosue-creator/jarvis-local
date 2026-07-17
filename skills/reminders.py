import threading
import time
import re
from datetime import datetime

memory = []
lock = threading.Lock()

def _reminder_thread(text: str, seconds: int):
    time.sleep(seconds)
    now = datetime.now().strftime("%H:%M")
    try:
        from rich.console import Console
        Console().print(f"\n[bold yellow]🔔 RECORDATORIO ({now}):[/bold yellow] {text}")
    except Exception:
        print(f"\n🔔 RECORDATORIO ({now}): {text}")
    # Avisar también por voz, para que se oiga aunque no mires la pantalla
    try:
        from output.voice_output import VoiceOutput
        vo = VoiceOutput()
        vo.enabled = True
        vo.speak(f"Recordatorio: {text}")
    except Exception:
        pass
    with lock:
        memory.append({"set": now, "for": text, "at": now})

def handle_reminder(text: str) -> str:
    t = text.lower()
    seconds = 0
    reminder_text = text
    patterns = [
        (r'(\d+)\s*s(ec(onds?)?)?\b', 1),
        (r'(\d+)\s*m(in(utes?)?)?\b', 60),
        (r'(\d+)\s*h(ou)?r?[s]?\b', 3600),
        (r'(\d+)\s*d(ay)?[s]?\b', 86400),
    ]
    for pattern, factor in patterns:
        match = re.search(pattern, t)
        if match:
            seconds += int(match.group(1)) * factor
    if seconds == 0:
        return "Say: remind me in 10 minutes to check the pizza"
    for p in [r'in \d+\s*s', r'in \d+\s*m', r'in \d+\s*h', r'in \d+\s*d',
             r'for \d+\s*s', r'for \d+\s*m', r'for \d+\s*h', r'for \d+\s*d']:
        t = re.sub(p, '', t)
    reminder_text = t.strip()
    for prefix in ["remind me to", "remind me that", "remind me"]:
        if reminder_text.startswith(prefix):
            reminder_text = reminder_text.replace(prefix, "", 1).strip()
    threading.Thread(target=_reminder_thread, args=(reminder_text, seconds), daemon=True).start()
    return f"Reminder set for {seconds}s: {reminder_text}"
