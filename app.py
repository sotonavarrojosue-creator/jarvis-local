#!/usr/bin/env python3
"""
JARVIS — Aplicación de escritorio.
Levanta el servidor Flask en segundo plano y abre una ventana nativa
(pywebview, sin navegador). Ejecutar: python app.py
"""

import os
import sys
import threading
import time
import socket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PORT = 5000


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_server():
    from webui.server import app
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


def main():
    if not _port_open(PORT):
        t = threading.Thread(target=start_server, daemon=True)
        t.start()
        # esperar a que Flask levante
        for _ in range(50):
            if _port_open(PORT):
                break
            time.sleep(0.2)

    url = f"http://127.0.0.1:{PORT}"

    try:
        import webview
        webview.create_window(
            "J.A.R.V.I.S.",
            url,
            width=1100,
            height=720,
            background_color="#0a0e17",
            min_size=(700, 500),
        )
        webview.start()
    except ImportError:
        # Fallback: abrir en el navegador si pywebview no está instalado
        print("pywebview no instalado — abriendo en el navegador.")
        print("Para ventana nativa: pip install pywebview")
        import webbrowser
        webbrowser.open(url)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
