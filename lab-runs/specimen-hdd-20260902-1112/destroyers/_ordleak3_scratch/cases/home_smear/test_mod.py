from pathlib import Path
MARKER = Path('/Users/annenpolka/.ordleak3-home.marker')

def test_a():
    MARKER.write_text("a", encoding="utf-8")

def test_b():
    assert not MARKER.exists(), MARKER.read_text(encoding="utf-8")
