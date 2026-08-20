# Gate on a value the rest of this fixture never constructs.

def dispatch(kind: str) -> str:
    if kind == "phoenix":
        return "rise"
    return "fall"


def known() -> list[str]:
    return ["eagle", "sparrow"]
