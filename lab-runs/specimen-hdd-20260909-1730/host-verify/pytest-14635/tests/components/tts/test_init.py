import pytest


@pytest.mark.parametrize("init_tts_cache_dir_side_effect", [OSError(2, "No access")])
@pytest.mark.parametrize("setup", ["mock_setup", "mock_config_entry_setup"], indirect=True)
def test_setup_component_no_access_cache_folder(hass, mock_tts_init_cache_dir, setup):
    assert hass == "hass"
    assert setup in ("mock_setup", "mock_config_entry_setup")
