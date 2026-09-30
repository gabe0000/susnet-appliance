from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from security_scan import scan_text


class SecurityScanTests(unittest.TestCase):
    def test_synthetic_material_passes(self):
        self.assertEqual(scan_text("TEST-1 uses 192.0.2.10 and no credentials"), [])

    def test_private_key_token_address_and_callsign_are_rejected(self):
        key = "-----BEGIN " + "OPENSSH PRIVATE KEY-----"
        token = "gh" + "p_" + ("A" * 35)
        callsign = "W" + "1ABC"
        public_address = ".".join(("8", "8", "8", "8"))
        findings = scan_text(f"{key}\n{token}\n{public_address}\n{callsign}")
        self.assertTrue(any("private-key" in item for item in findings))
        self.assertTrue(any("credential-like" in item for item in findings))
        self.assertTrue(any("IPv4" in item for item in findings))
        self.assertTrue(any("callsign" in item for item in findings))

    def test_assigned_password_is_rejected(self):
        label = "pass" + "word"
        self.assertTrue(scan_text(f'{label}="not-a-real-value"'))


if __name__ == "__main__":
    unittest.main()
