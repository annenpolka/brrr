def f():
    return 42

def test_container_literal():
    assert [1, 2, 3] == [1, 2, 4]

def test_callable_variable():
    assert f() == 100
