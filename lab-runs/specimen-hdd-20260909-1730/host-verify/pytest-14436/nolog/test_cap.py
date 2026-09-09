import logging

def test_caplog_at_level(caplog):
    with caplog.at_level(logging.WARNING):
        logging.warning("hi")
    assert "hi" in caplog.text
