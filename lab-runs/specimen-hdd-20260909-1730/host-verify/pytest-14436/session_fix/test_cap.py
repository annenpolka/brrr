import logging
import pytest

@pytest.fixture(scope="session")
def sess_cap(caplog):
    with caplog.at_level(logging.WARNING):
        yield caplog

def test_uses_session_caplog(sess_cap):
    logging.warning("hi")
    assert "hi" in sess_cap.text
