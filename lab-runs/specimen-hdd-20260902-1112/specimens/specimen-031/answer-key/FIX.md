# FIX (sealed)

pypa/pip PR 13703 / issue 13696.

Merge commit: 794c144edc1a6fdf1090d1fa633acd9bde822639
Title: Implement fallthrough logic for options

PR 12201 added a filename layer on configuration variants. That broke the old fallthrough in which a later empty user setting could clobber an earlier global setting.

Repair: `_get_ordered_configuration_items` first builds a dict per section so each key appears once (later variant wins, including empty), then converts to a list of pairs, dropping empty values only after the clobber. The empty user proxy therefore removes the global proxy rather than being skipped while the global value remains.

Tests: `test_user_config_overrides_global_config_with_empty_value` in tests/functional/test_configuration.py.

Do not expose this file to Dreamers, initial Red Pen, or initial Grounders.
