# Negative: string-edit near-misses must not become a class.
def ok(status: str) -> bool:
    return status == "success"


def fixtures() -> list[str]:
    return ["Success", "sucess", "pending"]
