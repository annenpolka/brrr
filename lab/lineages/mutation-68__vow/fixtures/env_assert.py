import os


def test_user_is_alice():
    # ran on alice   ← comment, not an oath
    assert os.environ["USER"] == "alice"
