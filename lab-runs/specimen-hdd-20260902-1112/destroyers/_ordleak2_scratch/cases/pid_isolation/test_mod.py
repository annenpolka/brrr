import os
from pathlib import Path

PIDFILE = Path('/tmp/ordleak2-pids.txt')

def test_a():
    PIDFILE.write_text(PIDFILE.read_text() + f"a {os.getpid()}\n" if PIDFILE.exists() else f"a {os.getpid()}\n")

def test_b():
    PIDFILE.write_text(PIDFILE.read_text() + f"b {os.getpid()}\n" if PIDFILE.exists() else f"b {os.getpid()}\n")
    assert True
