from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
    # failing revision:
    # error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]
