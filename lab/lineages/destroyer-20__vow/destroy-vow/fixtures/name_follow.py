import os
from pathlib import Path

def test_home():
    home = os.environ['HOME']
    expected = home
    got = Path.home().as_posix()
    assert got == expected
