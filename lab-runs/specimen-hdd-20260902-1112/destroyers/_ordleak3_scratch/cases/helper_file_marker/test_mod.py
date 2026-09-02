import helper
from pathlib import Path

def test_a():
    helper.MARKER.write_text("a", encoding="utf-8")
    helper.bucket.append("a")

def test_b():
    assert not helper.MARKER.exists(), "marker smeared"
    assert helper.bucket == [], helper.bucket
