import pytest

def test_handler_present(caplog):
    _ = caplog.handler

def test_handler_after_del(caplog):
    from _pytest.logging import caplog_handler_key
    del caplog._item.stash[caplog_handler_key]
    _ = caplog.handler
