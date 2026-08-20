# Default retry budget is 3 attempts.
# The hook timeout is 10 seconds.
MAX_RETRIES = 3
HOOK_TIMEOUT = 10
ENABLE_CACHE = True


def retry(fn, retries=MAX_RETRIES):
    last = None
    for _ in range(retries):
        last = fn()
        if last:
            return last
    return last
