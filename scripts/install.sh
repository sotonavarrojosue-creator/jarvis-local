#!/bin/bash
echo "JARVIS Install peagent"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$SCRIPT_DIR"

cd "$PROJ_DIR"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from example. Please edit it with your API keys."
    echo "OPENROUTER_API_KEY is required. The rest can be added later."
fi

python3 -m venv .venv 2>/dev/null || echo "venv skipped"

pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt

mkdir -p data/config data/memory data/notes data/obsidian

echo "JARVIS is ready. type 'python main.py' from the Proyectos/JARVIS/ directory."
