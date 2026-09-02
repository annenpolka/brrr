from pathlib import Path
MARK = Path(__file__).resolve().parent / "MARKER_SPLIT"

def test_a():
    MARK.write_text("a", encoding="utf-8")

def test_b():
    try:
        assert not MARK.exists()
    finally:
        if MARK.exists():
            MARK.unlink()
