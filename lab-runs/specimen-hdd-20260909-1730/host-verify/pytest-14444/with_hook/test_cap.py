import sys

def test_print_and_capsys(capsys):
    print("hello-stdout")
    print("hello-stderr", file=sys.stderr)
    captured = capsys.readouterr()
    assert "hello-stdout" in captured.out
    assert "hello-stderr" in captured.err
