"""Exercise the documented entrypoint without model requests or user images."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/quickstart.py"


class QuickstartTests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)

    def test_demo_exposes_drift_without_approving_or_calling_a_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "demo"
            result = self.invoke("--demo", "--out", out)
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((out / "quickstart.json").read_text())
            report = json.loads((out / summary["diagnostics"]).read_text())
            self.assertEqual(summary["providerCalls"], 0)
            self.assertFalse(summary["artworkGenerated"])
            self.assertFalse(summary["userApproved"])
            self.assertFalse(report["eligibleForPublication"])
            self.assertGreater(report["modes"][0]["sourceToCandidate"]["beyond2Fraction"], 0.1)
            self.assertTrue((out / summary["contactSheet"]).is_file())

    def test_real_inputs_are_unchanged_and_bound_by_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source, candidate = base / "original.png", base / "candidate.png"
            Image.new("RGB", (80, 80), "white").save(source)
            Image.new("RGB", (80, 80), "ivory").save(candidate)
            before = [p.read_bytes() for p in (source, candidate)]
            result = self.invoke("--source", source, "--candidate", candidate, "--out", base / "review")
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((base / "review/quickstart.json").read_text())
            for path, data, key in zip((source, candidate), before, ("source", "candidate")):
                self.assertEqual(path.read_bytes(), data)
                self.assertEqual(summary[key]["sha256"], hashlib.sha256(data).hexdigest())

    def test_existing_evidence_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "keep.txt"
            marker.write_text("existing evidence")
            result = self.invoke("--demo", "--out", directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), "existing evidence")
            self.assertEqual(list(Path(directory).iterdir()), [marker])

    def test_mismatched_dimensions_fail_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source, candidate = base / "original.png", base / "candidate.png"
            Image.new("RGB", (80, 80), "white").save(source)
            Image.new("RGB", (81, 80), "white").save(candidate)
            result = self.invoke("--source", source, "--candidate", candidate, "--out", base / "review")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("dimensions differ", result.stderr)
            self.assertFalse((base / "review").exists())

    def test_incomplete_arguments_have_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "review"
            result = self.invoke("--source", "missing.png", "--out", out)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
