import os
from pathlib import Path
HERE = Path(__file__).resolve().parent

def test_a():
    os.chdir("/tmp")

def test_b():
    assert Path.cwd() == HERE
