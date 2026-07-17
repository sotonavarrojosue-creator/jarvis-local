#!/usr/bin/env python3
"""
JARVIS WebUI - Standalone entry point for the Iron Man HUD interface.
Run: python webui.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from webui.server import app
from core.config import USER_NAME

if __name__ == "__main__":
    print(f"🤖 JARVIS WebUI starting for {USER_NAME}...")
    print("🌐 Interface available at: http://localhost:5000")
    print("⚡ Press Ctrl+C to stop")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)