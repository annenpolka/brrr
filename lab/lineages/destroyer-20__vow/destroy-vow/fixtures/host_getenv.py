import os

def test_host():
    assert os.environ['HOSTNAME'] == 'ci-mac-7'
