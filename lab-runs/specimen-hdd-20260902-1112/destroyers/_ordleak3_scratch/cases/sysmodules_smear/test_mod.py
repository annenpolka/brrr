import sys

def test_a():
    sys.modules["ordleak3_smear"] = type(sys)("ordleak3_smear")

def test_b():
    assert "ordleak3_smear" not in sys.modules, "smeared"
