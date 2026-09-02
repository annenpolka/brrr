import os
from pathlib import Path
home = Path.cwd()
def test_a():
    os.chdir("/tmp")
def test_b():
    assert Path.cwd() == home
