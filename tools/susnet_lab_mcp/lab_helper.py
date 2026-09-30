#!/usr/bin/env python3
"""Root-side fixed helper contract for a disposable qualification Pi.

Install as /usr/local/sbin/susnet-lab-helper and permit only this executable in
the restricted account's sudoers rule. Production action programs live under
/usr/local/libexec/susnet-lab-actions and accept bounded JSON on stdin.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ACTIONS = {
    "get_lab_identity",
    "get_hardware_inventory",
    "get_service_health",
    "get_sanitized_logs",
    "list_test_runs",
    "get_test_evidence",
    "install_candidate",
    "run_qualification_test",
    "reboot_test_pi",
    "restore_baseline",
    "run_guarded_rf_test",
    "flash_heltec_firmware",
}
ACTION_ROOT = Path("/usr/local/libexec/susnet-lab-actions")


def fail(reason: str) -> int:
    print(json.dumps({"state": "blocked", "reason": reason}))
    return 1


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ACTIONS:
        return fail("unknown action")
    raw = sys.stdin.read(8193)
    if len(raw) > 8192:
        return fail("request too large")
    try:
        request = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return fail("invalid request")
    if not isinstance(request, dict):
        return fail("request must be an object")
    executable = ACTION_ROOT / sys.argv[1]
    if not executable.is_file() or executable.is_symlink():
        return fail("fixed action is not provisioned")
    completed = subprocess.run(
        [str(executable)],
        input=json.dumps(request, separators=(",", ":")),
        text=True,
        capture_output=True,
        timeout=110,
        check=False,
        env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
    )
    if completed.returncode or len(completed.stdout) > 1_000_000:
        return fail("fixed action failed")
    sys.stdout.write(completed.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
