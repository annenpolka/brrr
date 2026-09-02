repository: systemd/systemd
issue: https://github.com/systemd/systemd/pull/43355
pr: https://github.com/systemd/systemd/pull/43355
failing_ref (parent of squash on main): cad2c455ec1acff29a81421c58adbe0ffc191f65
fixed_ref (reject leading/middle empty path components): f4284e9cebac67ad7af3bc27b736cf1107b88127
merged_at: 2026-08-13T15:27:10Z
pr_author: lionheartyu
merged_by: yuwata
changed_files: src/libsystemd/sd-path/path-lookup.c, src/libsystemd/sd-path/path-lookup.h, src/libsystemd/sd-path/sd-path.c, src/core/manager.c, src/analyze/analyze-verify-util.c, src/analyze/test-verify.c, src/test/test-path-lookup.c
pr_title: path-lookup: reject empty env path components
scout_note: not 010/031 env-empty-vs-unset. leftover cwd search-path identity from empty :: component. unique vs 001-148.
