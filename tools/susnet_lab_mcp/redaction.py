from __future__ import annotations

import ipaddress
import re
from typing import Any


SENSITIVE_KEY = re.compile(r"password|passwd|secret|token|private.?key|credential", re.IGNORECASE)
SENSITIVE_TEXT = (
    re.compile(r"(?i)\b(password|passwd|secret|token)\s*[=:]\s*\S+"),
    re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----", re.DOTALL),
)
IPV4 = re.compile(r"(?<![A-Za-z0-9])(?:\d{1,3}\.){3}\d{1,3}(?![A-Za-z0-9])")
SAFE_NETWORKS = tuple(ipaddress.ip_network(value) for value in ("127.0.0.0/8", "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))


def redact_text(value: str) -> str:
    output = value[:64_000]
    for pattern in SENSITIVE_TEXT:
        output = pattern.sub("[REDACTED]", output)
    def replace_ip(match: re.Match[str]) -> str:
        try:
            address = ipaddress.ip_address(match.group(0))
        except ValueError:
            return "[INVALID-IP]"
        return str(address) if any(address in network for network in SAFE_NETWORKS) else "[REDACTED-IP]"
    return IPV4.sub(replace_ip, output)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SENSITIVE_KEY.search(str(key)) else redact(child) for key, child in value.items()}
    if isinstance(value, list):
        return [redact(child) for child in value[:500]]
    if isinstance(value, str):
        return redact_text(value)
    return value
