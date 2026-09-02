import logging

def test_a():
    logging.getLogger("ordleak3").handlers.append(logging.NullHandler())

def test_b():
    assert logging.getLogger("ordleak3").handlers == []
