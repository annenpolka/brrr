import os


def test_hostname():
    assert os.environ["HOSTNAME"] == "ci-mac-7"
