from pkg_util import parse as leftover
from pkg_parse import parse as moved

seen = []

def test_a():
    seen.append(leftover("  z  "))

def test_b():
    assert seen == [], seen
