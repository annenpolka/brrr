from _pytest.raises import is_fully_escaped

cases = [
    r"\\.",
    r"\.",
    ".",
    "a",
    r"\\\\.",
    r"^\\.$",
]
for c in cases:
    print(repr(c), is_fully_escaped(c))
