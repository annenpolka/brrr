import sys

def test_dummy_test_with_traceback(request, capteesys):
    print("Hello world stdout", flush=True)
    print("Hello world stderr", file=sys.stderr, flush=True)
