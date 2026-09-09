# Host 実機 pytest#14323

Not Dreamer-facing. HOLD no View.

Comment snippet only (original issue body not in this dump):

    subprocess.Popen([sys.executable, "-c", "print('hello')"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

Host CPython 3.14.5 macOS.

| pytest | default | `--capture=fd` | `--capture=sys` | `-s` |
| --- | --- | --- | --- | --- |
| 8.4.1 | rc=0 | rc=0 | rc=0 | rc=0 |
| 9.0.1 | rc=0 | rc=0 | rc=0 | rc=0 |
| 9.0.3 | rc=0 | rc=0 | rc=0 | rc=0 |
| 9.1.0 | rc=0 | rc=0 | rc=0 | rc=0 |
| 9.1.1 | rc=0 | rc=0 | rc=0 | rc=0 |

Does not reproduce a capture/DEVNULL failure here. Commenter also could not reproduce on Windows 3.13.

Leftover `--setup-show`: **1 passed** on 8.4.1–9.1.1. `--setup-show` does not change DEVNULL. No View/export.

Leftover `--collect-only`: **1 collected** on 8.4.1–9.1.1. DEVNULL miss is execute. No View/export.
