from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from contracts import READ_TOOLS


PROTECTED = ("susnet", "commslab", "web01", "allstar01")


class FixtureBackend:
    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "get_lab_identity":
            return {"state": "ready", "lab_id": "fixture-pi", "role": "disposable-test-pi", "model": "Raspberry Pi 4B fixture", "image_sha256": "0" * 64, "rf_inhibited": True}
        if name == "get_hardware_inventory":
            return {"state": "ready", "usb": [{"role": "aursinc-fixture"}, {"role": "heltec-v3-fixture"}], "power": "fixture", "thermal_c": 42}
        if name == "get_service_health":
            return {"state": "ready", "services": [{"name": item, "status": "fixture"} for item in ("asterisk", "analog_bridge", "mmdvm_bridge", "susnet-aprs", "susnet-meshcore", "susnet-tts")]}
        if name == "get_sanitized_logs":
            return {"state": "ready", "service": arguments["service"], "lines": ["synthetic log line"]}
        if name == "list_test_runs":
            return {"state": "ready", "runs": [{"run_id": "fixture-run", "state": "complete", "artifact_sha256": "1" * 64}]}
        if name == "get_test_evidence":
            return {"state": "ready", "run_id": arguments["run_id"], "measurements": {"synthetic": True}, "attachments": []}
        if name in {"run_guarded_rf_test", "flash_heltec_firmware"}:
            return {"state": "requires_physical_action", "operation": name, "rf_inhibited": True}
        return {"state": "blocked", "operation": name, "reason": "fixture backend never mutates a system"}


class SSHBackend:
    def __init__(self) -> None:
        self.host = os.environ.get("SUSNET_LAB_HOST", "")
        self.user = os.environ.get("SUSNET_LAB_USER", "susnet-lab")
        self.expected_id = os.environ.get("SUSNET_LAB_EXPECTED_ID", "")
        self.known_hosts = os.environ.get("SUSNET_LAB_KNOWN_HOSTS", "")
        self.identity_file = os.environ.get("SUSNET_LAB_IDENTITY_FILE", "")
        self._validate_config()

    def _validate_config(self) -> None:
        lowered = self.host.lower()
        if not lowered.startswith("susnet-lab-") or any(item in lowered for item in PROTECTED):
            raise RuntimeError("lab host must be a dedicated susnet-lab-* host")
        if not self.expected_id or not self.known_hosts:
            raise RuntimeError("expected lab ID and pinned known-hosts file are required")
        known = Path(self.known_hosts)
        if not known.is_file() or known.is_symlink():
            raise RuntimeError("known-hosts file is missing or unsafe")
        if self.identity_file and not Path(self.identity_file).is_file():
            raise RuntimeError("identity file is missing")

    def _invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        command = [
            "ssh", "-T", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=yes", "-o", f"UserKnownHostsFile={self.known_hosts}",
            "-o", "ConnectTimeout=8",
        ]
        if self.identity_file:
            command.extend(("-i", self.identity_file))
        command.extend((f"{self.user}@{self.host}", "/usr/local/sbin/susnet-lab-helper", name))
        completed = subprocess.run(
            command,
            input=json.dumps(arguments, separators=(",", ":")),
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C"},
        )
        if completed.returncode:
            raise RuntimeError("lab helper refused or failed the operation")
        if len(completed.stdout) > 1_000_000:
            raise RuntimeError("lab response exceeded limit")
        result = json.loads(completed.stdout)
        if not isinstance(result, dict) or result.get("state") not in {"ready", "blocked", "requires_physical_action", "failed", "rolled_back", "complete"}:
            raise RuntimeError("lab returned an invalid structured state")
        return result

    def identity(self) -> dict[str, Any]:
        identity = self._invoke("get_lab_identity", {})
        if identity.get("lab_id") != self.expected_id or identity.get("role") != "disposable-test-pi":
            raise RuntimeError("lab identity mismatch")
        return identity

    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in READ_TOOLS:
            self.identity()
        return self._invoke(name, arguments)


def make_backend():
    return FixtureBackend() if os.environ.get("SUSNET_LAB_BACKEND") == "fixture" else SSHBackend()
