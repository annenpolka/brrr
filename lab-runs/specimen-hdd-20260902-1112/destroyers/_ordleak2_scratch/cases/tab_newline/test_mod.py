acc = []

def test_a():
    acc.append("a")

def test_b():
    raise AssertionError("tab\there\nand newline " + str(acc))
