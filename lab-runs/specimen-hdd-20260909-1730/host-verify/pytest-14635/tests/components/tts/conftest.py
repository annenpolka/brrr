import pytest


@pytest.fixture(autouse=True, name="mock_tts_cache_dir")
def mock_tts_cache_dir_fixture_autouse(mock_tts_cache_dir):
    return mock_tts_cache_dir
