import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / ".hidden"))
from helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
