import os, pathlib
p = pathlib.Path("pids.txt")
def test_a():
    p.write_text(str(os.getpid()) + "\n", encoding="utf-8")
def test_b():
    p.write_text(p.read_text(encoding="utf-8") + str(os.getpid()) + "\n", encoding="utf-8")
    assert False, "seen"
