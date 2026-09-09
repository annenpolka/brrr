# Host 実機 pytest#14935

Not Dreamer-facing. HOLD design. No View.

Two projects under a private `TMPDIR`. Default `tmp_path` retention (3). One run in proj-a, four runs in proj-b.

| pytest | remaining numbered dirs | `.origin` | proj-a `from-a.txt` left |
| --- | --- | --- | --- |
| 8.4.1 | `pytest-2,3,4` (user-scoped `pytest-of-<user>/`) | none | no |
| 9.0.1 | same `pytest-2,3,4` | none | no |
| 9.0.3 | same `pytest-2,3,4` | none | no |
| 9.1.0 | same `pytest-2,3,4` | none | no |
| 9.1.1 | same `pytest-2,3,4` | none | no |

Layout is user-scoped, not per-rootdir. Later proj-b runs evict proj-a scratch. No View/export.

Leftover extras (1× proj-a then 4× proj-b, isolated TMPDIR, 8.4.1–9.1.1 same):

| extra | from-a left | from-b left | note |
| --- | --- | --- | --- |
| unique `--basetemp` per project | 1 | 1 | `base-a/test_mark0/from-a.txt` kept; isolation works |
| shared `--basetemp` | 0 | 1 | same `test_mark0` path reused (not numbered `pytest-N`); from-a overwritten |
| `-o tmp_path_retention_count=10` | 1 | 4 | numbered `pytest-0..4`; count 10 keeps proj-a |
| `-o tmp_path_retention_count=0` | 0 | 0 | empty `pytest-of-<user>/` |
| `-o tmp_path_retention_policy=all` | 0 | 3 | still last 3 (`pytest-2,3,4`); policy=all does not override default count 3 |
| `-o tmp_path_retention_policy=none` | 0 | 0 | keep none |
| `--collect-only` | 0 | 0 | no tmp_path dirs created |

`--basetemp` unique per project keeps proj-a. Shared `--basetemp` overwrites the same `test_mark0` (different from numbered user-scoped eviction). Raising `tmp_path_retention_count` keeps proj-a under the default user-scoped layout. `policy=all` still respects count 3. HOLD design; no View/export.
