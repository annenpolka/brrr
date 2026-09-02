import os
from pathlib import Path

PIDFILE = Path('/tmp/ordleak4-pids.txt')

def _w(tag):
    prev = PIDFILE.read_text() if PIDFILE.exists() else ""
    PIDFILE.write_text(prev + f"{tag} {os.getpid()}\n")

def test_a():
    _w("a")

def test_b():
    _w("b")
    assert True
