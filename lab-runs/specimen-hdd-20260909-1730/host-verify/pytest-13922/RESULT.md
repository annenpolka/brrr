# Host 実機 pytest#13922 / #13910

Not Dreamer-facing. HOLD no View. Do not apply the PR.

CPython 3.14.5. `pytest -- test_ok.py extra_not_a_file` and the same under `python -W default`:

| pytest | rc | UserWarning `Do not expect file_or_dir` |
| --- | --- | --- |
| 8.4.1 | 4 | no; `file or directory not found: extra_not_a_file` |
| 9.0.1 | 4 | no; same ERROR |
| 9.0.3 | 4 | no; same ERROR |
| 9.1.0 | 4 | no; same ERROR |
| 9.1.1 | 4 | no; same ERROR |

Does not reproduce the argparse UserWarning here (comment suggested 3.12.3-only).

Leftover `--collect-only -- extra_not_a_file`: rc=4 `file or directory not found` on 8.4.1–9.1.1; no `Do not expect file_or_dir` UserWarning. Collect-only does not add the warning. No View/export.

Leftover `--setup-show -- extra_not_a_file`: rc=4 `file or directory not found` on 8.4.1–9.1.1; no argparse UserWarning. Same as collect-only. No View/export.

Leftover `--lf`/`--ff`/`--sw` (no extra path): **1 passed** on 8.4.1–9.1.1. The extra-path miss is argv, not last-failed. No View.

Leftover `--lf`/`--sw -- extra`: rc=4 both runs (`file or directory not found`). Leftover `--nf` (no extra): **1 passed**. Extra-path miss is not last-failed. No View.
