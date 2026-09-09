# Host 実機 pytest#14811

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Reuse of #14808 `ini_options` list-as-string `addini(type="string")`, plus implicit `type=None` (normalizes to string).

| setup | 8.4.1 | 9.0.1 | 9.1.1 |
| --- | --- | --- | --- |
| `type="string"` `-W default` | rc=1 AssertionError (list); **no warning** | same | same (also 9.0.3/9.1.0) |
| `type="string"` `-W error` | rc=1 AssertionError; not a warning-as-error | same | same |
| implicit type (`default="x"`) `-W default` | rc=1 AssertionError; no warning | — | rc=1 AssertionError; no warning |

The requested `PytestRemovedIn10Warning` is not present on 8.4.1–9.1.1. getini still returns a list.

Leftover `--collect-only` on `implicit/`: **1 collected** on 8.4.1–9.1.1. Collect-only does not execute `getini`, so the list-as-string AssertionError is not visible at collect.

Leftover `--setup-show` on `implicit/`: **1 failed** `isinstance(['not','a','string'], str)` on 8.4.1–9.1.1. `--setup-show` executes getini (collect-only hid it). No View/export.

Leftover `--tb=short`: **1 passed** on 8.4.1–9.1.1. The getini list-fail is `--setup-show` execute of `getini`, not a `--tb=short` failure. No View.

Leftover parent `--nf`/`--sw`: **1 passed** on 8.4.1–9.1.1 (getini list-fail lives in `implicit/`). No View.

Leftover `implicit/` `--ff`: still **1 failed** getini list `isinstance` on 8.4.1–9.1.1. No View.

Leftover `implicit/` `--maxfail=1`: still **1 failed** getini list. No View.
