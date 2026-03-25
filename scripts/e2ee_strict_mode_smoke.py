#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import socket


def post(url: str, token: str, payload: dict):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.getcode(), json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else "{}"
        try:
            obj = json.loads(body or "{}")
        except Exception:
            obj = {"raw": body}
        return e.code, obj


def wait_ready(url: str, token: str, timeout_s: int = 12):
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            req = urllib.request.Request(
                url.replace("/chat", "/e2ee/status"),
                headers={"Authorization": f"Bearer {token}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2) as r:
                if r.getcode() == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.3)
    return False


def main():
    if len(sys.argv) < 3:
        print("usage: e2ee_strict_mode_smoke.py <bridge_script.py> <ENV_PREFIX>", file=sys.stderr)
        sys.exit(2)

    bridge_script = os.path.abspath(sys.argv[1])
    env_prefix = sys.argv[2].strip().upper().replace("-", "_")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    token = "strict-smoke-token"

    tmpdir = tempfile.mkdtemp(prefix="e2ee-strict-smoke-")
    env = os.environ.copy()
    if env_prefix in ("OPENCLAW_APP", "OPENCLAW"):
        bridge_prefix = "OPENCLAW_APP"
        e2ee_prefix = "OPENCLAW_APP"
    elif env_prefix in ("AIGOR_APP", "AIGOR"):
        bridge_prefix = "AIGOR"
        e2ee_prefix = "AIGOR_APP"
    else:
        raise RuntimeError(f"unsupported ENV_PREFIX={env_prefix} (expected OPENCLAW_APP/OPENCLAW or AIGOR_APP/AIGOR)")

    env[f"{bridge_prefix}_BRIDGE_HOST"] = "127.0.0.1"
    env[f"{bridge_prefix}_BRIDGE_PORT"] = str(port)
    env[f"{bridge_prefix}_BRIDGE_TOKEN"] = token
    env[f"{e2ee_prefix}_E2EE_REQUIRED"] = "true"
    env[f"{e2ee_prefix}_E2EE_KEYSTORE"] = os.path.join(tmpdir, "keystore.json")
    env[f"{e2ee_prefix}_E2EE_RATCHET_STORE"] = os.path.join(tmpdir, "ratchet.json")
    env[f"{e2ee_prefix}_E2EE_OTK_STORE"] = os.path.join(tmpdir, "otk.json")

    proc = subprocess.Popen([sys.executable, bridge_script], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        url = f"http://127.0.0.1:{port}/chat"
        if not wait_ready(url, token):
            err = ""
            try:
                err = (proc.stderr.read() or b"").decode("utf-8", errors="ignore") if proc.stderr else ""
            except Exception:
                err = ""
            raise RuntimeError(f"bridge did not become ready on port {port}. stderr={err[-400:]}")

        cases = []

        # 1) no e2ee envelope
        c1 = post(url, token, {"sessionId": "smoke", "message": "hola"})
        cases.append(("missing_e2ee", c1[0] == 400 and c1[1].get("error") == "e2ee_required", c1))

        # 1b) invalid e2ee envelope type (must be object)
        c1b = post(url, token, {"sessionId": "smoke", "e2ee": []})
        cases.append(("invalid_e2ee_type", c1b[0] == 400 and c1b[1].get("error") == "e2ee_required", c1b))

        # 2) envelope without ciphertext
        c2 = post(url, token, {"sessionId": "smoke", "message": "hola", "e2ee": {}})
        cases.append(("missing_ciphertext", c2[0] == 400 and c2[1].get("error") == "e2ee_ciphertext_required", c2))

        # 2b) envelope with blank ciphertext (must be rejected)
        c2b = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "   "}})
        cases.append(("blank_ciphertext", c2b[0] == 400 and c2b[1].get("error") == "e2ee_ciphertext_required", c2b))

        # 2c) envelope with non-string ciphertext (must be rejected)
        c2c = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": 123}})
        cases.append(("invalid_ciphertext_type", c2c[0] == 400 and c2c[1].get("error") == "e2ee_ciphertext_required", c2c))

        # 3) encrypted envelope missing headerId
        c3 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x"}})
        cases.append(("missing_header", c3[0] == 400 and c3[1].get("error") == "e2ee_header_required", c3))

        # 4) encrypted envelope with non-string headerId (must be rejected)
        c4 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": 123}})
        cases.append(("invalid_header_type", c4[0] == 400 and c4[1].get("error") == "e2ee_header_required", c4))

        # 4b) encrypted envelope with null headerId (must be rejected)
        c4b = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": None}})
        cases.append(("null_header_rejected", c4b[0] == 400 and c4b[1].get("error") == "e2ee_header_required", c4b))

        # 5) encrypted envelope with blank-string headerId (must be rejected)
        c5 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "   "}})
        cases.append(("blank_header", c5[0] == 400 and c5[1].get("error") == "e2ee_header_required", c5))

        # 6) encrypted envelope missing positive counter
        c6 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1"}})
        cases.append(("missing_counter", c6[0] == 400 and c6[1].get("error") == "e2ee_counter_required", c6))

        # 7) encrypted envelope with non-integer counter
        c6 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": "abc"}})
        cases.append(("invalid_counter_type", c6[0] == 400 and c6[1].get("error") == "e2ee_counter_required", c6))

        # 7b) encrypted envelope with null counter (must be rejected)
        c6b = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": None}})
        cases.append(("null_counter_rejected", c6b[0] == 400 and c6b[1].get("error") == "e2ee_counter_required", c6b))

        # 8) encrypted envelope with numeric-string counter (must be rejected in strict mode)
        c7 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": "1"}})
        cases.append(("string_counter_rejected", c7[0] == 400 and c7[1].get("error") == "e2ee_counter_required", c7))

        # 8) encrypted envelope with bool counter (bool is int subclass in Python, must still be rejected)
        c8 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": True}})
        cases.append(("bool_counter_rejected", c8[0] == 400 and c8[1].get("error") == "e2ee_counter_required", c8))

        # 9) encrypted envelope with zero counter (must be positive)
        c9 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": 0}})
        cases.append(("zero_counter_rejected", c9[0] == 400 and c9[1].get("error") == "e2ee_counter_required", c9))

        # 10) encrypted envelope with negative counter (must be positive)
        c10 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": -1}})
        cases.append(("negative_counter_rejected", c10[0] == 400 and c10[1].get("error") == "e2ee_counter_required", c10))

        # 11) encrypted envelope with float counter (must be integer)
        c11 = post(url, token, {"sessionId": "smoke", "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": 1.5}})
        cases.append(("float_counter_rejected", c11[0] == 400 and c11[1].get("error") == "e2ee_counter_required", c11))

        # 12) clear attachment without e2eeAttachment
        c12 = post(
            url,
            token,
            {
                "sessionId": "smoke",
                "e2ee": {"ciphertext": "x", "headerId": "h-1", "counter": 1},
                "attachment": {"name": "a.txt", "mime": "text/plain", "dataBase64": "YQ=="},
            },
        )
        cases.append(("clear_attachment", c12[0] == 400 and c12[1].get("error") == "e2ee_attachment_required", c12))

        ok = all(x[1] for x in cases)
        out = {
            "ok": ok,
            "cases": [
                {
                    "name": name,
                    "pass": passed,
                    "status": data[0],
                    "error": data[1].get("error"),
                }
                for name, passed, data in cases
            ],
        }
        print(json.dumps(out, ensure_ascii=False), flush=True)
        sys.exit(0 if ok else 1)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
