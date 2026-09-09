import sys
def test_dummy():
    print("Hello world stdout", flush=True)
    print("Hello world stderr", file=sys.stderr, flush=True)
