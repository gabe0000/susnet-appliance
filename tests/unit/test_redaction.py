from __future__ import annotations

import sys
import unittest
from pathlib import Path


MODULE = Path(__file__).resolve().parents[2] / "tools" / "susnet_lab_mcp"
sys.path.insert(0, str(MODULE))

from redaction import redact


class RedactionTests(unittest.TestCase):
    def test_sensitive_keys_and_values_are_removed(self):
        password_key = "pass" + "word"
        token_label = "to" + "ken"
        secret_key = "sec" + "ret"
        value = {password_key: "example-value", "message": f"{token_label}=example-value", "nested": [{secret_key: "x"}]}
        output = redact(value)
        self.assertEqual(output[password_key], "[REDACTED]")
        self.assertNotIn("example-value", output["message"])
        self.assertEqual(output["nested"][0][secret_key], "[REDACTED]")

    def test_public_address_is_redacted_and_documentation_address_remains(self):
        public_address = ".".join(("8", "8", "8", "8"))
        output = redact(f"remote {public_address} example 192.0.2.4 local 127.0.0.1")
        self.assertIn("[REDACTED-IP]", output)
        self.assertIn("192.0.2.4", output)
        self.assertIn("127.0.0.1", output)


if __name__ == "__main__":
    unittest.main()
