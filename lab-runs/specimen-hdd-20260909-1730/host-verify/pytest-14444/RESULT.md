# Host 実機 pytest#14444

Not Dreamer-facing. HOLD feature. No View.

Wanted: force `--capture=sys` from `pytest_load_initial_conftests` by appending to `args`.

| setup | pytest | `option.capture` |
| --- | --- | --- |
| no hook, default CLI | 8.4.1 / 9.1.1 | `fd` |
| hook appends `--capture=sys` to `args` | 8.4.1 / 9.0.1 / 9.0.3 / 9.1.0 / 9.1.1 | still `fd` |
| hook also sets `known_args_namespace.capture` | 9.1.1 | still `fd` |
| `pytest_configure`: `config.option.capture = "sys"` | 8.4.1 / 9.0.1 / 9.0.3 / 9.1.0 / 9.1.1 | `sys` (assert passes) |

`capsys` tests pass either way under default capture. tractor/os.fork tree not cloned.

Leftover CLI `--capture=sys` on `no_hook/` (`test_mode.py`): **1 passed** on 8.4.1–9.1.1. The CLI flag sets capture; appending `--capture=sys` from `pytest_load_initial_conftests` does not.

Leftover `--setup-show --capture=sys` on `no_hook/` and `--setup-show` on `configure/`: **1 passed** on 8.4.1–9.1.1. `--setup-show` does not change capture. No View/export.

Leftover `--setup-plan` of `with_hook/` and `no_hook/`: 2 items, SETUP `capsys` + `pytestconfig`, no tests ran, 8.4.1–9.1.1. Plan does not show `option.capture` (fd vs sys is execute). No View.

Leftover `--collect-only` `with_hook/`: **2 collected** on 8.4.1–9.1.1. Capture fd vs sys is execute, not collect. No View.

Leftover `--collect-only` `no_hook/`: **2 collected** on 8.4.1–9.1.1. Capture fd vs sys is execute. No View.

Leftover CLI `--capture=sys` on `no_hook/`: **2 passed** on 8.4.1–9.1.1. CLI capture still works when the hook is absent. No View.

Leftover CLI `--capture=sys` on `with_hook/`: **2 passed** on 8.4.1–9.1.1. CLI still sets capture even when load_initial_conftests cannot. No View.
