#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ipaddress
import re
import sys
from pathlib import Path

from paths import ROOT, SUSNET_SCAN_ROOTS


PRIVATE_KEY = re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA|PRIVATE) PRIVATE KEY-----")
TOKEN_PATTERNS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[opsu]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\btskey-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),
)
IPV4 = re.compile(r"(?<![A-Za-z0-9])(?:\d{1,3}\.){3}\d{1,3}(?![A-Za-z0-9])")
CALLSIGN = re.compile(r"(?<![A-Z0-9])(?:[AKNW][A-Z]?\d[A-Z]{1,4})(?:-\d{1,2})?(?![A-Z0-9])", re.IGNORECASE)
CREDENTIAL_VALUE = re.compile(
    r"(?i)[\"']?(?:password|passwd|secret|api[_-]?key|auth[_-]?token)[\"']?\s*[:=]\s*[\"']([^\"'\s]{6,})"
)
ALLOWED_NETWORKS = tuple(
    ipaddress.ip_network(item)
    for item in ("0.0.0.0/32", "127.0.0.0/8", "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)


def iter_files(root: Path):
    roots = SUSNET_SCAN_ROOTS if root.resolve() == ROOT else (root,)
    for entry in roots:
        if not entry.exists():
            continue
        if entry.is_file():
            yield entry
            continue
        for path in entry.rglob("*"):
            if (
                path.is_file()
                and path.name != "security_scan.py"
                and not any(part in {"__pycache__", ".git", "build", ".venv"} for part in path.parts)
            ):
                yield path


def scan_text(text: str) -> list[str]:
    findings: list[str] = []
    if PRIVATE_KEY.search(text):
        findings.append("private-key material")
    for pattern in TOKEN_PATTERNS:
        if pattern.search(text):
            findings.append("credential-like token")
            break
    if CREDENTIAL_VALUE.search(text):
        findings.append("credential-like assigned value")
    for match in CALLSIGN.finditer(text):
        value = match.group(0).upper()
        if not value.startswith(("TEST", "DEMO")):
            findings.append(f"personal-looking callsign {value}")
    for match in IPV4.finditer(text):
        try:
            address = ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        if not any(address in network for network in ALLOWED_NETWORKS):
            findings.append(f"non-documentation IPv4 address {address}")
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=ROOT)
    args = parser.parse_args()
    findings: list[str] = []
    for path in iter_files(args.repository):
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for issue in scan_text(text):
            findings.append(f"{path}: {issue}")
    if findings:
        print("\n".join(findings), file=sys.stderr)
        return 1
    print("SusNet bootstrap secret and address scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
