def classify(path: str) -> str:
    if path.startswith("action."):
        return "action"
    return "other"


def samples() -> list[str]:
    return ["action.resolved-beam", "target.foo"]
