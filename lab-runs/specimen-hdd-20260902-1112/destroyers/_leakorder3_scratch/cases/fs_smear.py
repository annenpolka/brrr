from pathlib import Path
MARK = Path(__file__).resolve().parent / "MARKER_SMEAR"

def test_a():
    MARK.write_text("a", encoding="utf-8")

def test_b():
    assert not MARK.exists()
