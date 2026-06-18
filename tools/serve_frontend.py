#!/usr/bin/env python3
"""Serve the Repo-Analyser local frontend (no deploy — localhost only)."""

from __future__ import annotations

import argparse
import json
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
DEFAULT_PORT = 8765

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _json_response(handler: http.server.BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *handler_args, **kwargs):
        super().__init__(*handler_args, directory=str(FRONTEND), **kwargs)

    def log_message(self, fmt: str, *log_args) -> None:
        print(f"[frontend] {self.address_string()} - {fmt % log_args}", flush=True)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            _json_response(self, 200, {"ok": True, "service": "repo-analyser-frontend"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/pipeline/plan":
            self._handle_pipeline_plan()
            return
        self.send_error(404, "Not found")

    def _handle_pipeline_plan(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8"))
            repository_path = (body.get("repository_path") or "").strip()
            if not repository_path:
                _json_response(self, 400, {"ok": False, "error": "repository_path is required"})
                return

            from runtime.pipeline_plan import create_pipeline_plan

            plan = create_pipeline_plan(repository_path)
            _json_response(self, 200, plan)
        except ValueError as exc:
            _json_response(self, 400, {"ok": False, "error": str(exc)})
        except Exception as exc:
            _json_response(self, 500, {"ok": False, "error": f"Server error: {exc}"})


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

    url = f"http://127.0.0.1:{args.port}"
    with socketserver.TCPServer(("127.0.0.1", args.port), FrontendHandler) as httpd:
        print(f"Repo-Analyser UI → {url}", flush=True)
        print("Pipeline API → POST /api/pipeline/plan", flush=True)
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
