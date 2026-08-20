from src.profile import load_profile


def test_tmp_exists():
    load_profile("/tmp")
