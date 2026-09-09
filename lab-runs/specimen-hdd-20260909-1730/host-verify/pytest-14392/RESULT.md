# Host 実機 pytest#14392

Not Dreamer-facing. HOLD no View.

`from _pytest.raises import is_fully_escaped` on reporter cases (`r"\\."` and similar).

| pytest | `is_fully_escaped(r"\\.")` |
| --- | --- |
| 8.4.1 | True (reporter: wrong) |
| 9.0.1 | True |
| 9.0.3 | True |
| 9.1.0 | False |
| 9.1.1 | False |

Internal helper, not a sealed discovery View. No export.

Leftover extra patterns (`extra_cases.py`):

| pattern | 8.4.1 / 9.0.1 / 9.0.3 | 9.1.0 / 9.1.1 |
| --- | --- | --- |
| `r"\\."` | True | **False** |
| `r"\."` | True | True |
| `"."` | False | False |
| `"a"` | True | True |
| `r"\\\\."` | True | **False** |
| `r"^\\.$"` | False | False |

The 9.1.0 split is even-count backslash + dot (`r"\\."`, `r"\\\\."`). Single-backslash `r"\."` stays True. No View.
