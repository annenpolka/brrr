def test_mark(tmp_path):
    (tmp_path / "from-a.txt").write_text("a")
    assert (tmp_path / "from-a.txt").read_text() == "a"
