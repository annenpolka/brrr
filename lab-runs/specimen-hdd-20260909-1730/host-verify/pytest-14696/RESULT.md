# Host 実機 pytest#14696

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Mini from the PR description (no sqlalchemy tree): `tests/conftest.py` registers `--write-idents`; `test_it.py` at root; `idents.txt` exists.

| argv | 8.4.1 | 9.0.1 | 9.0.3 | 9.1.0 | 9.1.1 |
| --- | --- | --- | --- | --- | --- |
| `--write-idents idents.txt` | rc=4 unrecognized | rc=4 | rc=4 | rc=4 | rc=4 |
| `--write-idents nosuch-idents-file` | rc=0 1 pass | rc=0 | rc=0 | rc=4 unrecognized | rc=0 |
| `tests --write-idents idents.txt` | rc=5 no tests in `tests/` | same | same | same | same |
| `--write-idents idents.txt tests` | rc=5 no tests in `tests/` | same | same | same | same |
| `test_it.py --write-idents idents.txt` | rc=4 unrecognized | rc=4 | rc=4 | rc=4 | rc=4 |
| default `pytest` | rc=0 1 pass | rc=0 | rc=0 | rc=0 | rc=0 |

Existing file as the option value keeps `tests/conftest.py` off the initial-conftest path (unrecognized `--write-idents`) on every version tried. A missing filename loads the option except on 9.1.0 (test* initial-conftest gap; 9.1.1 loads it). Explicit `tests/` makes the option known but that directory has no `test_*.py`.

Leftover `pythonpath = tests`: existing `idents.txt` still unrecognized `--write-idents` on 8.4.1–9.1.1. Missing filename still 1 pass except 9.1.0 unrecognized. pythonpath does not change the existing-file option-value miss. No View/export. Related PRs stay 正解 off Dreamer.

Leftover parent collect `--write-idents idents.txt` (existing): unrecognized all versions. Parent missing-file collect hits leftover `alt_pp/` duplicate-addoption collisions except 9.1.0 unrecognized. Isolated `iso_miss/`: existing **and** missing both **9.1.0-only unrecognized**; 8.4.1/9.0.1/9.0.3/9.1.1 **1 collected**. Parent existing-file miss is leftover layout collision; isolated missing/existing both follow the 9.1.0 test* initial-conftest gap. No View/export.

Leftover isolated `iso_miss/` `--setup-show --write-idents missing-idents.txt`: 8.4.1/9.0.1/9.0.3/9.1.1 **1 passed**; 9.1.0 unrecognized. Leftover `--setup-show --write-idents idents.txt` after `touch idents.txt` (existing file as option value): unrecognized **all versions** including 8.4.1. Isolated existing-file miss matches the parent-tree writefile (not 9.1.0-only). No View/export.
