# winnow

Partition an uncommitted working tree into **wheat** (the smallest hunk set that reproduces a command's current behavior) and **chaff** (everything else).

This is `git bisect` for the dirty diff, not for commits.

## Install / run

Needs Python 3.9+ and `git`. No other dependencies.

```bash
chmod +x winnow
./winnow -- pytest tests/test_foo.py
python3 ./winnow --format paths -- pytest tests/test_foo.py
./demo.sh
```

The working tree is restored after the run (including on SIGINT). The git index is never touched.

## Examples

**1. Which hunk actually broke the test?**

```bash
./winnow -- python3 test.py
```

```
HEAD: exit=0 pass
WIP:  exit=1 AssertionError
wheat (1 units / 1 files):
  modify app.py  #2 @@ -10 +10 @@ def add(a, b):
chaff (3 units / 3 files):
  modify app.py  #1 @@ -1 +1 @@
  modify README.md  #1 @@ -1 +1 @@
  add    notes.txt  #1 (new file)
```

**2. Paths only, for pipelines**

```bash
./winnow --format paths -- python3 test.py
# app.py
```

**3. Wheat as a patch you can inspect or `git apply`**

```bash
./winnow --format patch -- python3 test.py > guilty.patch
```

On a real kizu checkout with mixed WIP (noise in README + a header comment in `src/app.rs` + a probe function at the bottom of `src/app.rs`), wheat was only the probe hunk:

```
--- a/src/app.rs
+++ b/src/app.rs
@@ -6126,3 +6126,5 @@
         );
     }
 }
+
+pub fn winnow_probe_marker() {}
```

## Flags

| flag | meaning |
| --- | --- |
| `-C DIR` | git repo (and command cwd) |
| `--cwd DIR` | command cwd only |
| `--base REF` | baseline (default `HEAD`) |
| `--granularity hunk\|file` | isolate hunks (default) or whole files |
| `--format text\|paths\|json\|patch` | output |
| `--fingerprint all\|strict\|stderr\|exit\|raw` | what "same behavior" means |
| `-v` | print each trial |
| `-q` | hide the chaff list in text mode |

Exit 0 on a successful partition (including "WIP does not affect this command"). Exit 2 for usage/tool errors. Exit 3 if the command is flaky.
