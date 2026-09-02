from pathlib import Path
M = Path("MARKER_SMEAR")
def test_a():
    M.write_text("a", encoding="utf-8")
def test_b():
    assert not M.exists()
