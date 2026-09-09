import pytest


@pytest.fixture
def init_tts_cache_dir_side_effect():
    return None


@pytest.fixture
def mock_tts_init_cache_dir(init_tts_cache_dir_side_effect):
    return init_tts_cache_dir_side_effect


@pytest.fixture
def mock_tts_cache_dir():
    return "parent"


@pytest.fixture
def hass():
    return "hass"


@pytest.fixture
def setup(request):
    return getattr(request, "param", "default")
