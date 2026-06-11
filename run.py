from __future__ import annotations

import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

try:
    import uvicorn
except ImportError:
    print("Uvicorn is not installed.")
    print("Run this command first:")
    print(f'"{sys.executable}" -m pip install -r requirements.txt')
    input("\nPress Enter to close...")
    raise SystemExit(1)


HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


def port_is_available() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((HOST, PORT)) != 0


def open_browser() -> None:
    webbrowser.open(URL)


def main() -> None:
    if not port_is_available():
        print(f"Port {PORT} is already in use.")
        print(f"The application may already be running at {URL}")
        input("\nPress Enter to close...")
        raise SystemExit(1)

    print("=" * 42)
    print("Kamchin Map")
    print("=" * 42)
    print(f"Open: {URL}")
    print("Press Ctrl+C to stop the server.\n")

    if "--no-browser" not in sys.argv:
        threading.Timer(1.5, open_browser).start()
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
