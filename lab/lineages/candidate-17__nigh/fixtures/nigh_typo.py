def ok(status: str) -> bool:
    return status == "success"


def fixtures() -> list[str]:
    # near-misses: case and a one-letter typo
    return ["Success", "sucess", "pending"]
