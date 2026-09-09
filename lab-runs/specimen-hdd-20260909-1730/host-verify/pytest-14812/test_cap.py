import logging


def test_x(caplog):
    logging.warning("hi")
    assert "hi" in caplog.text
