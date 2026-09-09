"""Drive shipped 2026-09-09 run-local gates (effective cap, contamination)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

RUN_SCRIPTS = Path(__file__).resolve().parents[1] / "lab-runs" / "corpus-hdd-20260909-1130" / "scripts"
sys.path.insert(0, str(RUN_SCRIPTS))

from test_run_gates import (  # noqa: E402
    ChainFilesTests,
    ClockGateTests,
    ContaminationTests,
    EffectiveCapTests,
    R1BudgetTests,
)


class ImportSurfaceTests(unittest.TestCase):
    def test_run_scripts_exist(self):
        self.assertTrue((RUN_SCRIPTS / "r1_budget.py").is_file())
        self.assertTrue((RUN_SCRIPTS / "contamination_check.py").is_file())
        self.assertTrue((RUN_SCRIPTS / "test_run_gates.py").is_file())


if __name__ == "__main__":
    unittest.main()
