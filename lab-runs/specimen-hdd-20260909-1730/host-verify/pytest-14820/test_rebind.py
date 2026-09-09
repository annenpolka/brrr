count = 0

def bump_count():
    global count
    count = 99
    return 0

def test_left_operand_is_read_too_late():
    assert count == bump_count()

value = "a"

def bump_value():
    global value
    value = "b"
    return "x"

def test_earlier_argument_is_read_too_late():
    assert (value, bump_value()) == ("a", "x")
