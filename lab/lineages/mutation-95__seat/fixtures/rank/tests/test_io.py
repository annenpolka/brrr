from src.io import fetch, read_cfg, load_home, record, paint, install


def test_fetch_beta():
    fetch("beta")


def test_read_beta():
    read_cfg("beta")


def test_home_beta():
    load_home("beta")


def test_record_default():
    record("y", duration=5)


def test_paint_beta():
    paint("beta")


def test_install_other():
    install("/tmp/other", "other")
