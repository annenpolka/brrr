import logging

def test_a():
    logging.getLogger("ordleak2").handlers.append(logging.NullHandler())

def test_b():
    assert logging.getLogger("ordleak2").handlers == []
