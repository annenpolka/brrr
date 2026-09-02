from pkg_util import parse as leftover
from pkg_parse import parse as moved

def test_a():
    leftover("  z  ")

def test_b():
    moved("  z  ")
