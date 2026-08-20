from src.connect import connect


def test_local():
    connect("localhost", timeout=30)


def test_default():
    connect("localhost")


def test_positional_same_world():
    # keyword vs positional must cluster as one world
    connect("localhost", 30)
