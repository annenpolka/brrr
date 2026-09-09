def test_getini(pytestconfig):
    val = pytestconfig.getini("mystr")
    assert isinstance(val, str)
