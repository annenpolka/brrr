# Host 実機 pytest#14635

Not Dreamer-facing. HOLD no View. Home Assistant core was **not** cloned.

Reduced pattern from the issue (transitive `parametrize` of `init_tts_cache_dir_side_effect`, autouse same-name `mock_tts_cache_dir` override, interleaved `water_heater` + `test_config_entries.py` + `tts/test_init.py`):

| pytest | interleaved collect | tts isolation | tts first | interleaved run |
| --- | --- | --- | --- | --- |
| 8.4.1 | rc=0 4 collected | rc=0 | rc=0 | rc=0 4 passed |
| 9.0.1 | rc=0 | rc=0 | rc=0 | rc=0 |
| 9.0.3 | rc=0 | rc=0 | rc=0 | rc=0 |
| 9.1.0 | rc=0 | rc=0 | rc=0 | rc=0 |
| 9.1.1 | rc=0 4 collected | rc=0 | rc=0 | rc=0 4 passed |

Does not reproduce `function uses no argument 'init_tts_cache_dir_side_effect'`. Reporter also could not reduce outside HA. No extra tree.

Leftover `--setup-show`: **4 passed** on 8.4.1–9.1.1. `--setup-show` does not produce the collection error. No View/export.

Leftover `--collect-only`: **4 collected** on 8.4.1–9.1.1. No HA collection error. No View/export.
