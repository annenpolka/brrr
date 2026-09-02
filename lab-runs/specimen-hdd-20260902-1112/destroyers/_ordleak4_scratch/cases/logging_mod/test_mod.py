import logging

def test_a():
    logging.getLogger("ordleak4").handlers.append(logging.NullHandler())

def test_b():
    assert logging.getLogger("ordleak4").handlers == []
