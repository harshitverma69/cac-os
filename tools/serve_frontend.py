#!/usr/bin/env python3
"""Serve the Repo-Analyser local frontend (no deploy — localhost only)."""

from __future__ import annotations

import argparse
import http.server
import socketserver
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
DEFAULT_PORT = 8765


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Repo-Analyser frontend on localhost")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-open", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    if not (FRONTEND / "index.html").is_file():
        print("Missing frontend/index.html — run: make build-frontend", flush=True)
        return 1

    data_file = FRONTEND / "data" / "skills.json"
    if not data_file.is_file():
        print("Missing frontend/data/skills.json — run: make build-frontend", flush=True)
        return 1

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *handler_args, **kwargs):
            super().__init__(*handler_args, directory=str(FRONTEND), **kwargs)

        def log_message(self, fmt: str, *log_args) -> None:
            print(f"[frontend] {self.address_string()} - {fmt % log_args}", flush=True)

    url = f"http://127.0.0.1:{args.port}"
    with socketserver.TCPServer(("127.0.0.1", args.port), Handler) as httpd:
        print(f"Repo-Analyser UI → {url}", flush=True)
        print("Skill runs appear under the Live runs tab when skill_finish write completes.", flush=True)
        print("Press Ctrl+C to stop.", flush=True)
        if not args.no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
