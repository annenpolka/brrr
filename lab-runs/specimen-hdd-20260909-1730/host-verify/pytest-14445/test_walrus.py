class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1


def test_walrus_in_assertion_basic():
    c = Counter()
    assert (before := c.value) == 0
    c.increment()
    assert before != (after := c.value)


def test_walrus_running_counter():
    count = 0
    items = []
    items.append("a")
    assert (count := count + 1) == len(items)
    items.append("b")
    assert (count := count + 1) == len(items)
    items.append("c")
    assert (count := count + 1) == len(items)
    assert count == 3
