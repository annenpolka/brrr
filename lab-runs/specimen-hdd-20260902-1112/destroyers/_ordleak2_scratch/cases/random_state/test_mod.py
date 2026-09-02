import random

def test_a():
    random.seed(123)
    random.random()

def test_b():
    # depends on prior consumption of the global RNG if seed not reset
    v = random.random()
    assert v == 0.0, v
