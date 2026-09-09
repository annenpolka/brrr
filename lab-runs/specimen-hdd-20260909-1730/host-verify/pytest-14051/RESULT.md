# Host 実機 pytest#14051

Not Dreamer-facing. HOLD no View.

`pytest.main(["test/", "--custom-arg", "custom/path/here"])` vs `"--custom-arg=..."`.

| pytest | space form | equals form |
| --- | --- | --- |
| 8.4.1 | rc=0 1 passed | rc=0 1 passed |
| 9.0.1 | rc=0 1 passed | rc=0 1 passed |
| 9.0.3 | rc=0 1 passed | rc=0 1 passed |
| 9.1.0 | rc=0 1 passed | rc=0 1 passed |
| 9.1.1 | rc=0 1 passed | rc=0 1 passed |

Does not reproduce the reporter's pytest 9 importError (sigstore-conformance tree).

Leftover `--collect-only`: **1 collected** on 8.4.1–9.1.1. Same as run.

Leftover `--setup-show`: **1 passed** on 8.4.1–9.1.1 (`test/test_a.py::test_ok`). `--setup-show` does not change the space/equals pass. No View/export.
