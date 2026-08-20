def load_user(uid: int) -> None:
    raise KeyError(f"user {uid} not found")


def connect(host: str, port: int) -> None:
    raise ConnectionError(f"cannot reach {host}:{port} after 3 retries")
