from pathlib import Path
M = Path("MARKER_LEAKORDER2")
def test_a():
    M.write_text("a", encoding="utf-8")
def test_b():
    seen = M.exists()
    if M.exists():
        M.unlink()
    assert not seen
