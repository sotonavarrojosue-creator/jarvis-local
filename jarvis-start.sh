#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
echo "🔧 Liberando puerto 5000..."
fuser -k 5000/tcp 2>/dev/null
sleep 1
echo "🚀 Arrancando JARVIS..."
"$DIR/.venv/bin/python" "$DIR/run_webui.py" &
PID=$!
sleep 2
xdg-open "http://localhost:5000" 2>/dev/null
echo "✅ JARVIS corriendo en http://localhost:5000 (PID: $PID)"
echo "⏎ Presiona Enter para cerrar..."
read -r
echo "🛑 Deteniendo JARVIS..."
kill $PID 2>/dev/null
wait $PID 2>/dev/null
echo "👋 Hasta luego"
