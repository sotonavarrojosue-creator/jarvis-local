#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
"$DIR/.venv/bin/python" "$DIR/run_webui.py" &
sleep 2
xdg-open "http://localhost:5000" 2>/dev/null
wait