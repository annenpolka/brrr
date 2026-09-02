KNOWN FIX (sealed): systemd/systemd PR 43355 squash f4284e9cebac67ad7af3bc27b736cf1107b88127.

failing_ref is parent cad2c455ec1acff29a81421c58adbe0ffc191f65.

get_paths_from_environ split empty SYSTEMD_UNIT_PATH components. Middle `::` became leftover cwd `.` in the unit search path. Unset / empty / trailing-colon / `::` were different identities; only trailing colon is append-defaults.

PR repair: path_is_valid_search_path rejects leading `:` and `::`. Generator path parse errors propagate.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
