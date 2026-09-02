bucket = set()


def test_write():
    bucket.add("w")


def test_empty():
    assert bucket == set(), bucket
