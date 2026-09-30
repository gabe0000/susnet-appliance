#!/usr/bin/env python3
from __future__ import annotations

import re
import sys

from paths import ROOT


REQUIREMENTS = {
    "packages": "M2-build-foundation",
    "image": "M2-build-foundation",
}


def milestone_status(text: str, milestone: str) -> str | None:
    block = re.search(
        rf"(?ms)^  - id: {re.escape(milestone)}\n(?P<body>.*?)(?=^  - id:|\Z)", text
    )
    if not block:
        return None
    status = re.search(r"(?m)^    status: (\w+)$", block.group("body"))
    return status.group(1) if status else None


def main() -> int:
    action = sys.argv[1] if len(sys.argv) == 2 else ""
    if action not in REQUIREMENTS:
        print(f"usage: {sys.argv[0]} <{'|'.join(REQUIREMENTS)}>", file=sys.stderr)
        return 2
    milestone = REQUIREMENTS[action]
    status = milestone_status((ROOT / "docs/IMPLEMENTATION_STATUS.yaml").read_text(), milestone)
    if status != "complete":
        print(f"{action} is blocked: {milestone} status is {status or 'missing'}", file=sys.stderr)
        return 1
    print(f"{action} gate is open; the implementation command must be supplied by {milestone}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
