import unittest
from pathlib import Path

FLAG = Path(__file__).with_name("_cleanup_flag.txt")


def _clean():
    FLAG.write_text("cleaned", encoding="utf-8")


def setUpModule():
    if FLAG.exists():
        FLAG.unlink()
    unittest.addModuleCleanup(_clean)


class TestU(unittest.TestCase):
    def test_one(self):
        self.assertTrue(True)
