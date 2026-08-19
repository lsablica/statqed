from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.registry import check_axiom_report


ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "theorem-registry/evidence/axioms.json"


class AxiomReportCheckerTests(unittest.TestCase):
    def test_live_structural_normalizer_report_verifies(self):
        check_axiom_report.verify(REPORT)

    def test_obsolete_normalizer_identifier_is_rejected(self):
        report = copy.deepcopy(json.loads(REPORT.read_text(encoding="utf-8")))
        report["declarations"][0]["normalizer"] = "statqed.lean-proposition.v0"
        with tempfile.TemporaryDirectory(prefix="statqed-registry-axiom-report-") as directory:
            path = Path(directory) / "axioms.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "registry.axiom_report_normalizer"):
                check_axiom_report.verify(path)


if __name__ == "__main__":
    unittest.main()
