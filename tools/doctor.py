#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys

from paths import BOOTSTRAP_FILES, ROOT


REQUIRED = ("git", "make", "python3", "ssh", "ssh-keygen")
OPTIONAL = ("docker", "xz")


def version(command: str) -> str:
    try:
        result = subprocess.run(
            [command, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    return (result.stdout or result.stderr).splitlines()[0][:160]


def main() -> int:
    missing_files = [str(path.relative_to(ROOT)) for path in BOOTSTRAP_FILES if not path.is_file()]
    commands = {name: shutil.which(name) for name in (*REQUIRED, *OPTIONAL)}
    py_ok = sys.version_info >= (3, 11)
    report = {
        "workspace": str(ROOT),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "python_supported": py_ok,
        "commands": commands,
        "versions": {name: version(name) for name in REQUIRED if commands[name]},
        "missing_bootstrap_files": missing_files,
        "native_arm64_image_builder": platform.system() == "Linux" and platform.machine() in {"aarch64", "arm64"},
        "lab_mcp_enabled_by_default": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    missing_required = [name for name in REQUIRED if not commands[name]]
    if missing_required:
        print(f"missing required commands: {', '.join(missing_required)}", file=sys.stderr)
    if not report["native_arm64_image_builder"]:
        print("note: package/image assembly must run on the dedicated ARM64 Linux builder", file=sys.stderr)
    return int(bool(missing_required or missing_files or not py_ok))


if __name__ == "__main__":
    raise SystemExit(main())
