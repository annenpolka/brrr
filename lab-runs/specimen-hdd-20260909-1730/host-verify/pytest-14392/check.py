from _pytest.raises import is_fully_escaped
cases = [
    (r"\\.", "two backslashes before dot"),
    ("\\\\|", "four backslashes before pipe as python str"),
    (r"\\\\.", "four backslashes before dot raw"),
]
for s, label in cases:
    print(repr(s), label, "->", is_fully_escaped(s))
