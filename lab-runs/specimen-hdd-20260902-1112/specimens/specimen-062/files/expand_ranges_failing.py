# Reduced excerpt of expand_ranges on failing_ref
# src/tox/config/loader/ini/factor.py

return re.sub(
    r"""
    (                       # outer capture group
        ( \d+ ) - ( \d+ )   # closed range: start-end
        |
        ( \d+ ) -           # right-open range: start-
        |
        (?<= [{,] ) - ( \d+ )  # left-open range: -end (preceded by { or ,)
        |
        \d+                 # single number
    )
    (?: , | \} )            # followed by comma or closing brace
    """,
    _expand,
    value,
    flags=re.VERBOSE,
)
