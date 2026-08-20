def parse(name: str, n: int) -> None:
    raise ValueError(f"unknown dialect {name!r} at line {n}")


def static() -> None:
    print("static exact message from fixtures")
