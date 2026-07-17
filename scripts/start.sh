#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

FLAGS=""
if [ "$1" == "--voice" ] || [ "$1" == "-v" ]; then
    FLAGS="$FLAGS --voice"
fi
if [ "$1" == "--web" ] || [ "$1" == "-w" ]; then
    FLAGS="$FLAGS --web"
fi
if [ "$2" == "--web" ] || [ "$2" == "-w" ]; then
    FLAGS="$FLAGS --web"
fi

python main.py $FLAGS
