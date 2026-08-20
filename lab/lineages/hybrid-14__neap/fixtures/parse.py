def parse(rest, x=1, ready=True, enabled=True):
    if not ready:
        return None
    if x > 0:
        return "ok"
