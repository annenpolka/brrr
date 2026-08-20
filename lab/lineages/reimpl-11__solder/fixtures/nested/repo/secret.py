def leak(k: str) -> None:
    raise RuntimeError(f"nested secret key {k} leaked")
