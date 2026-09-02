import os
from pathlib import Path
LOG = Path(__file__).resolve().parent / "pids.txt"
acc = []

def test_a():
    LOG.write_text(LOG.read_text() + f"a {os.getpid()}\n" if LOG.exists() else f"a {os.getpid()}\n")
    acc.append("a")

def test_b():
    LOG.write_text(LOG.read_text() + f"b {os.getpid()}\n" if LOG.exists() else f"b {os.getpid()}\n")
    assert acc == [], acc
