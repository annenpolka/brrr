import logging
def test_log():
    logging.getLogger("hdd3062").warning("hello-log")
    assert True
