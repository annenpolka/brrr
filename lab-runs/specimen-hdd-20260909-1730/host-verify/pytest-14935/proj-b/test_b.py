def test_mark(tmp_path):
    (tmp_path / "from-b.txt").write_text("b")
    assert (tmp_path / "from-b.txt").read_text() == "b"
