import pytest

def test_raises_pattern_mismatch():
    with pytest.raises(ValueError, match="nope"):
        raise ValueError("actual")
