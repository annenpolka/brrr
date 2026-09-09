# Host 実機 pytest#14094 MonkeyPatch spelling control

Not Dreamer-facing. HOLD no View. Correct `pytest.MonkeyPatch` spelling is a host control; it was not passed to a Dreamer.

Public snippet as written used `pytest.Monkeypatch` (AttributeError on all versions). This mini uses the public API name.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | 1 passed (`delitem` existing restored); 2 failed (`delitem` missing `{1: 3}`; `delattr` missing `prop=3`) |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same |
| 9.1.0 | 1 | same |
| 9.1.1 | 1 | same |

Matches the reporter's restore bug once the class name is spelled correctly. No 8/9 delta.

Leftover `--tb=short`: still 2 failed / 1 passed (`delitem` missing `{1: 3}`; `delattr` missing `prop=3`) on 8.4.1–9.1.1.

Leftover `--setup-show test_delitem.py`: same 2 failed / 1 passed on 8.4.1–9.1.1. `--setup-show` does not restore deleted keys/attrs. No View/export.

Leftover `--lf`: seed 2 failed 1 passed then `--lf` **2 failed** (reruns fails only). Leftover `--ff`: 2 failed 1 passed both runs. Leftover `--sw`: first 1 failed 1 passed interrupted; second 1 failed 1 deselected (hides later fail). No View.

Leftover `--nf`: still 2 failed 1 passed. Leftover `--maxfail=1`: seed 2 failed 1 passed then **1 failed 1 passed** (hides later fail). No View.
