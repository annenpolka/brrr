import unittest
from contextlib import contextmanager
from pathlib import Path

FLAG = Path(__file__).with_name("_enter_flag.txt")


@contextmanager
def _cm():
    FLAG.write_text("entered", encoding="utf-8")
    try:
        yield
    finally:
        FLAG.write_text("exited", encoding="utf-8")


def setUpModule():
    if FLAG.exists():
        FLAG.unlink()
    unittest.enterModuleContext(_cm())


class TestE(unittest.TestCase):
    def test_one(self):
        self.assertTrue(True)
