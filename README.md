# JARVIS Local

Local voice assistant with 12+ skills, WebUI, wake word detection, and plugin system.

## Features

- **Voice Pipeline** — Wake word → STT (Whisper) → LLM → TTS (Edge-TTS)
- **12+ Built-in Skills** — Weather, Notes, Calculator, DateTime, Web Search, Spotify, Telegram, Reminders, Translator, News, IP/Geo, File Manager, System Control
- **WebUI** — Chat interface at `localhost:8080`
- **Plugin System** — Drop-in skill modules
- **Persistent Memory** — Session-based conversation history
- **Local-First** — Runs entirely on your machine (no cloud required for core)

## Skills Included

| Skill | Description |
|-------|-------------|
| `weather.py` | Current weather via Open-Meteo |
| `notes.py` | Save/read/delete notes |
| `calculator.py` | Math expressions |
| `datetime_skill.py` | Date/time queries |
| `web_search.py` | DuckDuckGo search |
| `spotify.py` | Playback control |
| `telegram.py` | Send messages |
| `reminders.py` | Set/get reminders |
| `translator.py` | Multi-language translation |
| `news.py` | Latest headlines |
| `ip_geo.py` | IP geolocation |
| `file_manager.py` | File operations |
| `system_control.py` | System commands |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run
python main.py

# 4. Open WebUI
# http://localhost:8080
```

## Project Structure

```
jarvis-local/
├── main.py                 # Entry point
├── app.py                  # FastAPI + WebUI
├── server.py               # HTTP server
├── run_webui.py            # WebUI launcher
├── requirements.txt
├── install.sh              # Systemd installer
├── jarvis.sh               # CLI launcher
├── jarvis-start.sh         # Start script
├── jarvis-desktop.sh       # Desktop entry
├── PLAN.md                 # Architecture plan
├── BUGS_Y_PLAN.md          # Bug tracker
├── input/
│   ├── voice_input.py      # Whisper STT
│   ├── wake_word.py        # Wake word detection
│   └── text_input.py       # Text fallback
├── output/
│   ├── voice_output.py     # Edge-TTS
│   └── text_output.py      # Text fallback
├── skills/                 # 12+ skill modules
│   ├── __init__.py
│   ├── skill_manager.py
│   ├── weather.py
│   ├── notes.py
│   ├── calculator.py
│   ├── datetime_skill.py
│   ├── web_search.py
│   ├── spotify.py
│   ├── telegram.py
│   ├── reminders.py
│   ├── translator.py
│   ├── news.py
│   ├── ip_geo.py
│   ├── file_manager.py
│   └── system_control.py
├── webui/                  # WebUI templates
└── obsidian_logger.py      # Obsidian vault logging
```

## Tech Stack

- **Python** 3.11+
- **FastAPI** — Web server
- **Whisper** — Local STT (tiny model)
- **Edge-TTS** — High-quality TTS
- **OpenRouter** — LLM access (GPT-4o-mini, etc.)
- **WebRTC VAD** — Voice activity detection

## License

MIT
