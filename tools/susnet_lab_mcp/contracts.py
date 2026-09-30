from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


READ_TOOLS = {
    "get_lab_identity",
    "get_hardware_inventory",
    "get_service_health",
    "get_sanitized_logs",
    "list_test_runs",
    "get_test_evidence",
}
WRITE_TOOLS = {
    "install_candidate",
    "run_qualification_test",
    "reboot_test_pi",
    "restore_baseline",
    "run_guarded_rf_test",
    "flash_heltec_firmware",
}
ALL_TOOLS = READ_TOOLS | WRITE_TOOLS

SERVICES = ("asterisk", "analog_bridge", "mmdvm_bridge", "susnet-aprs", "susnet-meshcore", "susnet-tts")
QUALIFICATION_TESTS = (
    "usb-inventory",
    "alsa-loopback",
    "dv-switch-startup",
    "aprs-fixture",
    "meshcore-serial",
    "tts-offline",
    "reboot-recovery",
)
RF_TESTS = ("ptt-polarity", "dummy-load-audio", "transmit-timeout")
REBOOT_REASONS = ("qualification", "recovery-test", "baseline-restore")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
TOKEN = re.compile(r"^[A-Z2-9]{8,32}$")


@dataclass(frozen=True)
class ToolSpec:
    description: str
    schema: dict[str, Any]
    read_only: bool
    destructive: bool = False

    def mcp(self, name: str) -> dict[str, Any]:
        return {
            "name": name,
            "description": self.description,
            "inputSchema": self.schema,
            "annotations": {
                "readOnlyHint": self.read_only,
                "destructiveHint": self.destructive,
                "idempotentHint": self.read_only,
                "openWorldHint": False,
            },
        }


EMPTY = {"type": "object", "properties": {}, "additionalProperties": False}


def obj(properties: dict[str, Any], required: tuple[str, ...]) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}


TOOLS: dict[str, ToolSpec] = {
    "get_lab_identity": ToolSpec("Return the dedicated test Pi identity and RF safety state.", EMPTY, True),
    "get_hardware_inventory": ToolSpec("Return sanitized USB, serial, audio, power, and thermal inventory.", EMPTY, True),
    "get_service_health": ToolSpec("Return status for the fixed SusNet service allowlist.", EMPTY, True),
    "get_sanitized_logs": ToolSpec(
        "Return bounded redacted logs for one allowed service.",
        obj(
            {
                "service": {"type": "string", "enum": list(SERVICES)},
                "minutes": {"type": "integer", "minimum": 1, "maximum": 60},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            ("service",),
        ),
        True,
    ),
    "list_test_runs": ToolSpec("List qualification run IDs, states, and artifact hashes.", EMPTY, True),
    "get_test_evidence": ToolSpec(
        "Return structured measurements and attachment hashes for one run.",
        obj({"run_id": {"type": "string", "pattern": IDENTIFIER.pattern}}, ("run_id",)),
        True,
    ),
    "install_candidate": ToolSpec(
        "Install one signed build from the lab's approved artifact store.",
        obj(
            {"build_id": {"type": "string", "pattern": IDENTIFIER.pattern}, "sha256": {"type": "string", "pattern": SHA256.pattern}},
            ("build_id", "sha256"),
        ),
        False,
        True,
    ),
    "run_qualification_test": ToolSpec(
        "Run one enumerated non-transmitting qualification test.",
        obj({"test": {"type": "string", "enum": list(QUALIFICATION_TESTS)}}, ("test",)),
        False,
    ),
    "reboot_test_pi": ToolSpec(
        "Reboot only the verified disposable test Pi.",
        obj({"reason": {"type": "string", "enum": list(REBOOT_REASONS)}}, ("reason",)),
        False,
        True,
    ),
    "restore_baseline": ToolSpec(
        "Restore one approved pinned test-Pi baseline.",
        obj({"baseline_id": {"type": "string", "pattern": IDENTIFIER.pattern}}, ("baseline_id",)),
        False,
        True,
    ),
    "run_guarded_rf_test": ToolSpec(
        "Run one bounded RF test after console authorization and safety checks.",
        obj(
            {
                "test": {"type": "string", "enum": list(RF_TESTS)},
                "physical_token": {"type": "string", "pattern": TOKEN.pattern},
                "max_seconds": {"type": "integer", "minimum": 1, "maximum": 10},
            },
            ("test", "physical_token", "max_seconds"),
        ),
        False,
        True,
    ),
    "flash_heltec_firmware": ToolSpec(
        "Flash an approved Heltec V3 firmware hash after physical authorization.",
        obj(
            {
                "device": {"type": "string", "enum": ["heltec-v3"]},
                "firmware_sha256": {"type": "string", "pattern": SHA256.pattern},
                "physical_token": {"type": "string", "pattern": TOKEN.pattern},
            },
            ("device", "firmware_sha256", "physical_token"),
        ),
        False,
        True,
    ),
}


def validate_arguments(name: str, arguments: object) -> dict[str, Any]:
    if name not in TOOLS:
        raise ValueError("unknown tool")
    if not isinstance(arguments, dict):
        raise ValueError("arguments must be an object")
    schema = TOOLS[name].schema
    properties = schema.get("properties", {})
    unknown = set(arguments) - set(properties)
    if unknown:
        raise ValueError(f"unknown argument: {sorted(unknown)[0]}")
    missing = set(schema.get("required", [])) - set(arguments)
    if missing:
        raise ValueError(f"missing argument: {sorted(missing)[0]}")
    result = dict(arguments)
    for key, value in result.items():
        rule = properties[key]
        if rule.get("type") == "string":
            if not isinstance(value, str) or len(value) > 128:
                raise ValueError(f"invalid {key}")
            if "enum" in rule and value not in rule["enum"]:
                raise ValueError(f"unsupported {key}")
            if "pattern" in rule and not re.fullmatch(rule["pattern"], value):
                raise ValueError(f"invalid {key}")
        elif rule.get("type") == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"invalid {key}")
            if value < rule.get("minimum", value) or value > rule.get("maximum", value):
                raise ValueError(f"out-of-range {key}")
    return result
