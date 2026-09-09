def identity(value):
    return value

def collect(*values):
    return values

def test_compare_preserves_pre_walrus_left_value():
    value = "Hello"
    assert value != identity(value := value.lower())
    assert value == "hello"

def test_call_preserves_earlier_positional_argument():
    value = "Hello"
    assert collect(value, identity(value := value.lower())) == (
        "Hello",
        "hello",
    )
    assert value == "hello"

def test_failed_compare_uses_pre_walrus_left_value():
    value = 2
    try:
        assert value == identity(value := 3)
    except AssertionError:
        pass
    else:
        raise AssertionError("assertion was rewritten as 3 == 3")
    assert value == 3
