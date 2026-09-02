import sys

def test_a():
    sys.modules["ordleak2_smear"] = type(sys)("ordleak2_smear")

def test_b():
    assert "ordleak2_smear" not in sys.modules, "smeared"
