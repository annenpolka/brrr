import subprocess
import sys

def test_popen_devnull_fails():
    p = subprocess.Popen(
        [sys.executable, "-c", "print('hello')"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    p.wait()
    assert p.returncode == 0
