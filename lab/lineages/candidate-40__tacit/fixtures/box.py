def greet(name, greeting="hi", times=1):
    return greeting * times


class Box:
    def __init__(self, width, height=10, label="box"):
        self.width = width


from dataclasses import dataclass


@dataclass
class Cfg:
    timeout: int = 30
    retries: int = 3


def use():
    greet("x")
    greet("x", "yo")
    greet("x", times=2)
    Box(1)
    Box(1, height=10)
    Box(1, height=20, label="crate")
    Cfg()
    Cfg(timeout=30)
    Cfg(timeout=5)
