#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = os.environ.get("AIGOR_BRIDGE_HOST", "0.0.0.0")
PORT = int(os.environ.get("AIGOR_BRIDGE_PORT", "8091"))
TOKEN = os.environ.get("AIGOR_BRIDGE_TOKEN", "")
DEFAULT_SESSION = os.environ.get("AIGOR_BRIDGE_SESSION", "aigor-app-chat")


def extract_json_block(text: str):
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_str = False
    esc = False
    end = -1

    for idx in range(start, len(text)):
        ch = text[idx]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = idx + 1
                break

    if end == -1:
        return None

    candidate = text[start:end]
    try:
        return json.loads(candidate)
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/chat":
            self._send(404, {"ok": False, "error": "Not found"})
            return

        if TOKEN:
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {TOKEN}":
                self._send(401, {"ok": False, "error": "Unauthorized"})
                return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            data = json.loads(raw or "{}")
        except Exception:
            self._send(400, {"ok": False, "error": "Bad JSON"})
            return

        message = (data.get("message") or "").strip()
        session_id = (data.get("sessionId") or DEFAULT_SESSION).strip() or DEFAULT_SESSION
        if not message:
            self._send(400, {"ok": False, "error": "message required"})
            return

        cmd = [
            "openclaw", "agent",
            "--session-id", session_id,
            "--message", message,
            "--json",
        ]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            out = (proc.stdout or "") + (proc.stderr or "")
            parsed = extract_json_block(out)
            if proc.returncode != 0 or not parsed:
                self._send(500, {"ok": False, "error": "agent_failed", "details": out[-600:]})
                return

            reply = ""
            payloads = (((parsed.get("result") or {}).get("payloads")) or [])
            if payloads and isinstance(payloads, list):
                first = payloads[0] or {}
                reply = (first.get("text") or "").strip()
            if not reply:
                reply = "(Sense resposta textual)"

            self._send(200, {"ok": True, "reply": reply, "sessionId": session_id})
        except subprocess.TimeoutExpired:
            self._send(504, {"ok": False, "error": "timeout"})
        except Exception as e:
            self._send(500, {"ok": False, "error": str(e)})


def main():
    srv = HTTPServer((HOST, PORT), Handler)
    print(f"AIGOR bridge listening on http://{HOST}:{PORT}/chat")
    srv.serve_forever()


if __name__ == "__main__":
    main()
