# Host 実機 pytest#14591

Not Dreamer-facing. HOLD for HDD consumer (no View/export). Bisect SHA from the issue is 正解 and is not recorded here for the consumer.

- pytest 8.4.1: 4 passed
- pytest 9.0.1: 4 passed
- pytest 9.0.3: 4 passed
- pytest 9.1.0: collection error `duplicate parametrization of 'myfixture'`
- pytest 9.1.1: rc=0 (host refute; still HOLD, no View)

Leftover `--collect-only`: same split (8.4.1–9.0.3/9.1.1 **4 collected**; 9.1.0 rc=2 `duplicate parametrization of 'myfixture'`). Same as run.

Leftover `--setup-show`: same split (8.4.1–9.0.3/9.1.1 4 passed; 9.1.0 duplicate at collect).

Leftover `--tb=short`: same split (8.4.1–9.0.3/9.1.1 4 passed; 9.1.0 collection `duplicate parametrization of 'myfixture'`). `--tb=short` does not change collect errors. No View.

Leftover `--setup-plan test_myfixture.py`: 8.4.1/9.0.1/9.0.3/9.1.1 4 items. **9.1.0** collect ERROR `duplicate parametrization of 'myfixture'`. Same collect split as run. No View.

Leftover `--lf` after duplicate-param collect (isolated cache, explicit file): 8.4.1/9.1.1 4 pass; `--lf` no last-failed. **9.1.0** collect ERROR duplicate; `--lf` still collect ERROR (collect failures are not last-failed). `--lf` does not skip the 9.1.0 collect miss. No View.

Leftover `--ff` after duplicate-param collect: 8.4.1/9.1.1 4 pass; `--ff` no last-failed. **9.1.0** collect ERROR duplicate; `--ff` still collect ERROR (not last-failed). No View.
