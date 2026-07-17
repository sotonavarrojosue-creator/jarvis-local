# JARVIS Local

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-orange?logo=openai)](https://github.com/openai/whisper)

Local voice assistant with 12+ skills, WebUI, wake word detection, and plugin system.

## Features

- **Voice Input** — Whisper (tiny/base) for speech-to-text
- **Wake Word** — Energy-based + WebRTC VAD detection
- **Voice Output** — Edge-TTS with multiple voices
- **WebUI** — Chat interface at `localhost:8080`
- **12+ Skills** — Weather, notes, calculator, datetime, web search, Spotify, Telegram, translator, reminders, file manager, news, IP geo, system control
- **Plugin System** — Extensible skill architecture
- **Session Memory** — Persistent conversation history
- **Obsidian Logging** — Auto-logs to vault

## Skills Included

| Skill | Description |
|-------|-------------|
| `weather.py` | Current weather via Open-Meteo |
| `notes.py` | Save/read/delete notes |
| `calculator.py` | Math expressions |
| `datetime_skill.py` | Date/time queries |
| `web_search.py` | DuckDuckGo search |
| `spotify.py` | Spotify control |
| `telegram.py` | Telegram bot bridge |
| `translator.py` | Multi-language translation |
| `reminders.py` | Timed reminders |
| `file_manager.py` | File operations |
| `news.py` | News headlines |
| `ip_geo.py` | IP geolocation |
| `system_control.py` | System commands |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run
python main.py          # CLI mode
python run_webui.py     # WebUI mode

# 4. Or install as service
./jarvis-start.sh
```

## Project Structure

```
jarvis-local/
├── main.py                 # CLI entry point
├── run_webui.py            # WebUI entry point
├── server.py               # FastAPI server for WebUI
├── webui.py                # WebUI components
├── requirements.txt
├── install.sh              # Systemd installer
├── jarvis.sh               # Launcher script
├── .env.example
├── input/
│   ├── voice_input.py      # Whisper + VAD
│   ├── text_input.py       # Text fallback
│   ├── wake_word.py        # Wake word detection
│   └── display.py          # Terminal HUD
├── output/
│   ├── voice_output.py     # Edge-TTS
│   └── text_output.py      # Text fallback
├── skills/                 # 12+ skill modules
├── core/
│   ├── skill_manager.py    # Skill registry
│   └── session.py          # Session memory
└── obsidian_logger.py      # Vault logging
```

## Tech Stack

- **Python** 3.11+
- **Whisper** (speech-to-text)
- **Edge-TTS** (text-to-speech)
- **WebRTC VAD** (voice activity detection)
- **FastAPI** (WebUI backend)
- **OpenRouter** / **Ollama** (LLM)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | **Yes** | Get from [openrouter.ai/keys](https://openrouter.ai/keys) |
| `OPENROUTER_MODEL` | No | Default: `openai/gpt-4o-mini` |
| `OLLAMA_HOST` | No | Default: `http://localhost:11434` |
| `OLLAMA_MODEL` | No | Default: `llama3.1:8b` |
| `WHISPER_MODEL` | No | Default: `tiny` |
| `WHISPER_LANGUAGE` | No | Default: `es` |
| `TTS_ENGINE` | No | Default: `edge-tts` |
| `TTS_VOICE` | No | Default: `es-ES-AlvaroNeural` |
| `TELEGRAM_BOT_TOKEN` | No | For Telegram bridge |
| `TELEGRAM_CHAT_ID` | No | Your chat ID |
| `WEBUI_HOST` / `WEBUI_PORT` | No | Default: `0.0.0.0:8080` |

## License

MIT
