from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from reference_collector import collect


class CollectorTests(unittest.TestCase):
    def test_allowlisted_synthetic_json_is_collected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            output = root / "output"
            path = source / "system/packages.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"source": "synthetic", "packages": []}))
            hashes = collect(source, output)
            self.assertEqual(hashes[0][0], "system/packages.json")
            self.assertTrue((output / "system/packages.json").is_file())

    def test_secret_field_and_unknown_file_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            source.mkdir()
            label = "pass" + "word"
            (source / "system").mkdir()
            (source / "system/packages.json").write_text(json.dumps({label: "canary-value"}))
            with self.assertRaises(ValueError):
                collect(source, Path(temp) / "out")
            (source / "unknown.txt").write_text("synthetic")
            with self.assertRaises(ValueError):
                collect(source, Path(temp) / "out")


if __name__ == "__main__":
    unittest.main()
