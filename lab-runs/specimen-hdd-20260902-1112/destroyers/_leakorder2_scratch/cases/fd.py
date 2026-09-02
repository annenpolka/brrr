import os
def test_a():
    os.environ["X"] = "1"
    open("fd_mark", "w").write("a")
def test_b():
    assert not os.path.exists("fd_mark")
