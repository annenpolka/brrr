# Ambient 0 is a sentinel bound, not a HIT on == 0, unless field-qualified.
def empty(n: int) -> bool:
    return n == 0


def positive(n: int) -> bool:
    return n > 0
