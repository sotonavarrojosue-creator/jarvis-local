#!/usr/bin/env python3
"""WebUI runner - keeps Flask server alive"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import MISSING_KEYS

if MISSING_KEYS:
    print(f"⚠ Missing API keys: {', '.join(MISSING_KEYS)} — configúrala desde ⚙ en la WebUI")

from webui.server import app

if __name__ == "__main__":
    print("JARVIS WebUI http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)