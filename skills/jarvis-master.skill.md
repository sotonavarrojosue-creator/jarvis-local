# JARVIS — Iron Man Edition

Skill de opencode para el proyecto JARVIS, asistente de IA personal al estilo Iron Man.

## Proyecto

- **Ubicación:** `/mnt/datos/RESPALDO/OBSIIDIAN/prueba_de_claude/Proyectos/JARVIS/`
- **Entry point:** `main.py` con flags `--voice` y `--web`
- **Plan:** `/mnt/datos/RESPALDO/OBSIIDIAN/prueba_de_claude/Proyectos/JARVIS_PLAN.md`
- **Registrado en:** `Proyectos/VARIOS.md`

## Arquitectura

```
JARVIS/
├── main.py              # Entry point (argparse: --voice, --web)
├── obsidian_logger.py   # Log conversaciones al vault Obsidian
├── .env.example         # Variables de entorno (NUNCA hardcodear keys)
├── requirements.txt     # Dependencias (simpleeval>=1.0.5 obligatorio por CVE)
├── .gitignore           # Excluye .env, __pycache__, data/, .venv/
├── core/
│   ├── config.py        # Env vars, settings.json, MISSING_KEYS
│   ├── brain.py         # Brain class: think() sync, think_stream() streaming
│   └── memory.py        # Sesiones JSON en data/memory/
├── input/
│   ├── text_input.py    # Prompt >~ estilizado
│   ├── voice_input.py   # SpeechRecognition + Whisper tiny
│   └── wake_word.py     # Whisper wake word threaded
├── output/
│   ├── display.py       # Boot animation, HUD panels, neon cyan/yellow/green
│   ├── voice_output.py  # edge-tts con toggle
│   └── text_output.py
├── skills/
│   ├── skill_manager.py # SkillManager: 13 skills + plugin loader
│   ├── system_control.py # Linux GNOME: xdg-open, nautilus, gnome-*
│   ├── datetime_skill.py
│   ├── calculator.py    # simpleeval (CVE-2026-32640 mitigado)
│   ├── notes.py
│   ├── web_search.py    # DuckDuckGo
│   ├── weather.py       # Open-Meteo
│   ├── translator.py    # deep-translator
│   ├── ip_geo.py        # ip-api
│   ├── news.py          # DuckDuckGo headlines
│   ├── reminders.py
│   ├── file_manager.py
│   ├── spotify.py       # Placeholder (requiere API keys)
│   ├── telegram.py      # Placeholder (requiere bot token)
│   └── plugins/         # Auto-loaded via __import__
├── webui/
│   ├── server.py        # Flask + SSE + sync endpoint
│   └── templates/
│       └── index.html   # HUD Iron Man aesthetic
├── scripts/
│   ├── install.sh       # Setup
│   ├── start.sh         # Launcher
│   └── jarvis.service   # systemd user service
└── data/
    ├── config/settings.json
    ├── memory/session_*.json
    └── obsidian/logs/jarvis_YYYY-MM-DD.md
```

## Reglas de desarrollo

- **OS:** Linux GNOME — usar `xdg-open`, `nautilus`, `gnome-terminal`, etc. NUNCA comandos Windows.
- **API keys:** Solo en `.env` o variables de entorno. Nunca en código.
- **Idioma:** Español por defecto. USER_NAME=Aaron.
- **Streaming:** `brain.think_stream()` con Rich Live para CLI; `brain.think()` sync para WebUI.
- **Skills:** Detección por keyword matching. Plugins en `skills/plugins/`.
- **Seguridad:** `system_control.py` tiene whitelist de comandos + blocked patterns.
- **simpleeval:** Versión >=1.0.5 obligatoria (CVE-2026-32640 critical).
- **Obsidian:** Log en `data/obsidian/logs/`, vinculado desde VARIOS.md.
- **Servicios gratuitos:** OpenRouter free tier, edge-tts, Whisper local, DuckDuckGo, Open-Meteo, deep-translator, ip-api.

## Comandos útiles

```bash
python main.py           # Modo texto
python main.py --voice   # Modo voz + texto
python main.py --web     # Modo texto + WebUI en :5000
pip install -r requirements.txt
bash scripts/install.sh
```

## Dependencias clave

- `openai` (OpenRouter compatible)
- `rich` (display HUD)
- `flask` (WebUI)
- `edge-tts` (voz)
- `SpeechRecognition` + `whisper` (input voz)
- `duckduckgo_search` (búsquedas)
- `deep-translator` (traducción)
- `simpleeval>=1.0.5` (calculadora segura)
