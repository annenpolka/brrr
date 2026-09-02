from enum import Enum
class Color(Enum):
    RED = []
def test_a():
    Color.RED.value.append("a")
def test_b():
    assert Color.RED.value == [], Color.RED.value
