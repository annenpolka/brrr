import os

timeout = os.environ.get("WAIT")


def connect():
    timeout = os.environ["WAIT"]
    return timeout
