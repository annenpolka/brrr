def test_raises_the_wrong_error():
    assert 1 < 0 < 1 / 0

def test_calls_what_it_should_not():
    calls = []
    def boom():
        calls.append("boom")
        return 5
    try:
        assert 1 < 0 < boom()
    except AssertionError:
        pass
    assert calls == []
