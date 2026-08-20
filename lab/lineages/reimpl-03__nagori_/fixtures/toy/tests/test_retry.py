from src.retry import MAX_RETRIES, HOOK_TIMEOUT, ENABLE_CACHE


def test_defaults():
    assert MAX_RETRIES == 3
    assert HOOK_TIMEOUT == 10
    assert ENABLE_CACHE is True
