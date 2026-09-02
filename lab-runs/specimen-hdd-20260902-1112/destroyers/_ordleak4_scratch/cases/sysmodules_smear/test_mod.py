import sys

def test_a():
    sys.modules["ordleak4_smear"] = type(sys)("ordleak4_smear")

def test_b():
    assert "ordleak4_smear" not in sys.modules, "smeared"
