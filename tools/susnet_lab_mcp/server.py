#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from backend import make_backend  # noqa: E402
from contracts import TOOLS, WRITE_TOOLS, validate_arguments  # noqa: E402
from redaction import redact  # noqa: E402


STATE_DIR = Path(os.environ.get("SUSNET_LAB_STATE_DIR", HERE.parents[1] / ".susnet-lab"))


def emit(message: dict) -> None:
    sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def audit(name: str, arguments: dict, state: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = STATE_DIR / "audit.jsonl"
    safe_arguments = {key: "[PRESENT]" if "token" in key else value for key, value in arguments.items()}
    event = {
        "at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "tool": name,
        "arguments": safe_arguments,
        "state": state,
    }
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(descriptor, (json.dumps(event, separators=(",", ":")) + "\n").encode())
    finally:
        os.close(descriptor)


def call_tool(backend, name: str, arguments: object) -> dict:
    validated = validate_arguments(name, arguments)
    lock_handle = None
    try:
        if name in WRITE_TOOLS:
            STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
            lock_handle = (STATE_DIR / "mutation.lock").open("a+")
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        result = redact(backend.call(name, validated))
        state = str(result.get("state", "failed"))
        audit(name, validated, state)
        return {"content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}], "structuredContent": result, "isError": state == "failed"}
    except Exception as exc:
        result = {"state": "failed", "error": str(exc)[:300]}
        audit(name, validated, "failed")
        return {"content": [{"type": "text", "text": json.dumps(result)}], "structuredContent": result, "isError": True}
    finally:
        if lock_handle:
            lock_handle.close()


def handle(message: dict, backend) -> dict | None:
    method = message.get("method")
    request_id = message.get("id")
    if request_id is None:
        return None
    if method == "initialize":
        result = {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "susnet-lab", "version": "0.1.0"},
            "instructions": "Dedicated disposable test-Pi instruments only. Read tools return sanitized data. Mutations are allowlisted, audited, serialized, and RF/flash actions require physical authorization. Never target live SusNet or other infrastructure.",
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [spec.mcp(name) for name, spec in TOOLS.items()]}
    elif method == "tools/call":
        params = message.get("params", {})
        result = call_tool(backend, params.get("name", ""), params.get("arguments", {}))
    else:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "method not found"}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main() -> int:
    try:
        backend = make_backend()
    except Exception as exc:
        print(f"susnet-lab startup refused: {exc}", file=sys.stderr)
        return 1
    for raw in sys.stdin:
        if len(raw) > 1_000_000:
            continue
        try:
            message = json.loads(raw)
            response = handle(message, backend)
            if response:
                emit(response)
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            emit({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": str(exc)[:200]}})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
