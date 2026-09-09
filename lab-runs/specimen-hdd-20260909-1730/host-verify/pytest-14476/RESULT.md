# Host 実機 pytest#14476

Not Dreamer-facing. HOLD no View.

Dummy `test_baidu_search` / `test_baidu_logo` / `test_other`.
`pytest --collect-only -k "baidu and not logo"`:

| pytest | rc | collected |
| --- | --- | --- |
| 8.4.1 | 0 | `test_baidu_search` only |
| 9.0.1 | 0 | same |
| 9.0.3 | 0 | same |
| 9.1.0 | 0 | same |
| 9.1.1 | 0 | same |

Does not reproduce a `-k` mismatch. No View/export.

Leftover comment mini `-k foo` with `@pytest.mark.foo` on `test_x` and a `test_foo` name: collects **both** on 8.4.1–9.1.1 (UnknownMarkWarning). Matches the comment. Still HOLD.

Leftover `--collect-only -k foo test_kfoo.py`: **2 collected** (`test_x` + `test_foo`) on 8.4.1–9.1.1 with UnknownMarkWarning. Collect-only matches run. No View.


Leftover `--setup-show -k foo test_kfoo.py`: **2 passed**, 1 UnknownMarkWarning on 8.4.1–9.1.1. `--setup-show` matches collect. No View.

Leftover `--tb=short -k foo test_kfoo.py`: **2 passed**, 1 UnknownMarkWarning on 8.4.1–9.1.1. No View.
