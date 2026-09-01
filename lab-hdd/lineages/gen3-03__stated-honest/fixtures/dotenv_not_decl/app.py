"""Hardcoded timeout. .env is env-layer, not another declaration."""

timeout = 10


def connect():
    return timeout
