# DESTROYER pairaxis 2

Date: 2026-09-02 15:38 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pairaxis/pairaxis`

sha256 `b6ea93737f885bd5b9b452511323db2cf88c75c1ffb1f87762ba953f1d398ba7` (2180 bytes, 73 lines). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/pairaxis-pairaxis/pairaxis/pairaxis.py` is byte-identical (HEAD `2cff07700105c3ea8bd5bde6282780e1cf22aa1c`, branch `specimen-hdd/pairaxis-pairaxis`). Parent `main` is `432f954`; `git ls-tree HEAD pairaxis` is empty. No tests, no `CANDIDATE.md`. Host Python 3.14.5. `command -v poetry` empty. `command -v pytest` empty. Neither is in the source. No merge onto `main`. Worktree was not edited.

Origin (`hdd-origins/hdd-transfer-silent.md` / specimen-017): given two otherwise-similar pair traces, name the one field that explains pass vs fail. Kind: USEFUL_COMPOSITION. Harvest smallest artifact: “CLI that diffs two pair records and emits the only differing key.” Research boundary: does not run a package solver. Analog `specimens/specimen-017/files/pair_extras.py` already prints `only_axis requires_contains_extra_dep`.

First destroyer (`DESTROYER_pairaxis.md`) **KEEP** as a paired-specimen lens. Missing files rc=2; identical `only_axis none` / `n_diff 0`; two diffs `only_axis multiple` without inventing a single axis; unseen pair names `recognized`. Primitive: “Does not run the underlying tools; diffs caller-supplied traces. That is honest for paired specimens.” MUTATE leftover was “refuse `only_axis multiple` without listing diffs (it already lists them).” `MUTATE.md` (job-0327) was a **no-op**. Bytes unchanged. That writeup already named the fork: KEEP the lens, or **KILL as a thin dict-diff of caller-supplied traces**. First KEEP is not protection.

This candidate is a **THIN_WRAPPER of dict-diff of caller traces**. `n_diff` is `len(diffs)`. `only_axis` is `none` / the first differing key / the token `multiple`. Host replica of `parse_record` + `maybe_literal` + key-union inequality is **byte-identical** to CLI stdout on **36/36** host cases (`stdout_eq=True`, `rc_eq=True`). The same predicate matches `n_diff` / `only_axis` on **36/36**. `diff` of the owned three-line records already names the two lines. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pairaxis/pairaxis
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pairaxis/fixtures
S017=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-017/files/pair_extras.py
S072=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-072/files/run_orders_extra.py
```

Host-executed against the archive only. Do not merge onto `main`. Do not run poetry / pytest / django. Do not wrap a solver or a test runner to escape THIN_WRAPPER. Do not send this diff back to R1. Sibling `leakorder` / `ordleak` already own order-leak execution. Transfer “OK onto pairaxis” is this same dict-diff of traces the caller already wrote.

---

## What still works

Owned 017 pair, unseen rename of `recognized`, identical records, swapped owned pair, missing path, directory, no args. `demo.sh` ×2, archived `demo-1.log` / `demo-2.log` byte-identical, wrapper exit 0. That is the first KEEP. It is also `diff` of two caller files plus a label.

```bash
python3 "$CLI" "$FIX/pair_a.rec" "$FIX/pair_b.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen_a.rec" "$FIX/unseen_b.rec"; echo rc=$?
python3 "$CLI" "$FIX/pair_a.rec" "$FIX/pair_a.rec"; echo rc=$?
```

```text
fields 3
n_diff  2
only_axis  multiple
diff  requires_contains_extra_dep  left=true  right=false
diff  resolved_extra_deps  left=["B"]  right=[]
rc=0

fields 3
n_diff  1
only_axis  recognized
diff  recognized  left=["B"]  right=["C"]
rc=0

fields 3
only_axis  none
n_diff  0
rc=0
```

Missing path / directory / `-` / `/dev/null` / `/dev/stdin` / FIFO / process substitution `<(cat …)`: `pairaxis: file not found` rc=2 (`Path.is_file()` only). No args / one arg / extra arg: argparse rc=2. `--help` rc=0. Symlink and a filename with a space: same owned harvest, rc=0.

That is the whole useful delta.

---

## Implementation

Load-bearing body:

```python
left = parse_record(left_path.read_text(encoding="utf-8"))
right = parse_record(right_path.read_text(encoding="utf-8"))
keys = sorted(set(left) | set(right))
diffs = [(k, left.get(k, "<absent>"), right.get(k, "<absent>"))
         for k in keys
         if maybe_literal(left.get(k, "<absent>")) != maybe_literal(right.get(k, "<absent>"))]
print(f"n_diff  {len(diffs)}")
print(f"only_axis  {diffs[0][0] if len(diffs) == 1 else 'multiple'}")
```

`maybe_literal` is `ast.literal_eval` or the original string. `parse_record` accepts tab / `=` / space, last-wins on duplicate keys, skips `#` and blanks. Source contains no `poetry`, `pytest`, `django`, `subprocess`, `importlib`, `runpy`. `main` never sees a test, a lockfile, or a solver. Exit is 0 whenever both paths are regular files, including `n_diff 4`.

---

## Attacks

### 1. THIN_WRAPPER of dict-diff of caller traces

Independent reconstruction of `parse_record` + `maybe_literal` + the print format (no import of the CLI as a package) is **byte-identical** to CLI stdout on 36/36 host cases, including path lines:

| case | n_diff | only_axis | stdout_eq | rc |
| --- | ---: | --- | --- | ---: |
| owned pair | 2 | multiple | True | 0 |
| unseen pair | 1 | recognized | True | 0 |
| identical | 0 | none | True | 0 |
| swap owned | 2 | multiple | True | 0 |
| one axis `b` | 1 | b | True | 0 |
| three axes | 3 | multiple | True | 0 |
| s072-shaped traces | 4 | multiple | True | 0 |
| silentadd cursor traces | 1 | cursor | True | 0 |
| empty / comments-only | 0 | none | True | 0 |
| list quote-form | 0 | none | True | 0 |
| `1` vs `1.0` | 0 | none | True | 0 |
| `False` vs `0` | 0 | none | True | 0 |
| key named `none` | 1 | none | True | 0 |
| key named `multiple` | 1 | multiple | True | 0 |

`n_diff` / `only_axis` predicate (no formatter): **36/36** match.

```text
n = len(diffs)
only = "none" if n == 0 else (diffs[0] if n == 1 else "multiple")
```

Owned / unseen / identical: `match=True`.

Nearest ordinary workflow, host-executed:

```bash
diff -u "$FIX/pair_a.rec" "$FIX/pair_b.rec"
comm -3 <(sort "$FIX/pair_a.rec") <(sort "$FIX/pair_b.rec")
python3 "$S017"
```

```text
-resolved_extra_deps	["B"]
-requires_contains_extra_dep	true
+resolved_extra_deps	[]
+requires_contains_extra_dep	false

requires_contains_extra_dep	false
requires_contains_extra_dep	true
resolved_extra_deps	["B"]
resolved_extra_deps	[]

pair_A_fresh_requires recognized ['B'] resolved_extra_deps ['B'] PASS
pair_B_pruned_requires recognized ['B'] resolved_extra_deps [] FAIL
only_axis requires_contains_extra_dep
```

Harvest said “diff shows many lines; the remainder is naming the axis.” The owned records are three lines. `diff` already names both differing keys. The analog **hardcodes** `only_axis requires_contains_extra_dep` while two fields differ. pairaxis lists those two keys and writes `multiple`. The remainder is a label on a dict-diff the caller already extracted. pairaxis never ran `pair_extras.py`.

Constitution: a THIN_WRAPPER does not gain extra `diff KEY left=… right=…` rows to escape classification. Listing the keys is the dict-diff. Swallowing them was the leftover this lineage already refused (job-0327 no-op). Concatenating them into a fake single axis was that job’s kill condition. Both escapes are still this primitive.

### 2. `only_axis` is a token, not an execution axis

A record whose only differing key is named `none`:

```text
n_diff  1
only_axis  none
diff  none  left=1  right=2
rc=0
```

Identical owned records:

```text
only_axis  none
n_diff  0
rc=0
```

`only_axis none` is not “no diffs.” A key named `multiple` with `n_diff 1` prints `only_axis multiple` — the same token as `n_diff 2` on the owned pair. The column cannot be a pipe predicate for “single axis” or “identical.”

Silentadd-shaped traces that share `status=ok` and `collision` and differ only in `cursor` (the hybrid claim):

```text
n_diff  1
only_axis  cursor
diff  cursor  left=1  right=2
rc=0
```

That is `n==1` so the first (only) key name is printed. `lineages/hybrid-pairaxis-silentadd.md` already said this is not a new binary. It is this dict-diff.

TRANSFER_s072 (`hdd-extraglobal`): host traces taken from `run_orders_extra.py` PASS vs FAIL:

```text
fields 4
n_diff  4
only_axis  multiple
diff  acc  left=[]  right=['a']
diff  flag  left=False  right=True
diff  order  left=('test_b', 'test_a')  right=('test_a', 'test_b')
diff  test_b  left=PASS  right=FAIL
rc=0
```

Transfer “holds” because the caller wrote four keys. pairaxis did not run the orders. `run_orders_extra.py` already prints `acc_after`, `flag_after`, and the FAIL. leakorder’s miss on nested tests is not this object’s join; this object never loaded a test module.

### 3. `ast.literal_eval` hides string-form diffs the harvest would count

| left | right | n_diff | only_axis |
| --- | --- | ---: | --- |
| `["B"]` | `['B']` | 0 | none |
| `1` | `1.0` | 0 | none |
| `False` | `0` | 0 | none |
| `{'a': 1}` | `{"a": 1}` | 0 | none |
| `true` | `True` | 1 | flag |

`true` is not a Python literal, so it stays a string and diffs against `True`. Owned fixtures use lowercase `true`/`false`; they never become bools. `1 == 1.0` and `False == 0` are Python, not pair-trace equality. Quote-form of the same list is `n_diff 0`. The “axis” can vanish without the records matching as text. `diff` of those files still shows a line. The CLI reports none.

Duplicate keys last-wins. Mixed tab/`=`/`space` forms of the same key collapse. Trailing whitespace is `strip()`’d away (`n_diff 0`). BOM on the first key splits `k` vs `\ufeffk` into `n_diff 2` / `only_axis multiple`. Invalid UTF-8: raw `UnicodeDecodeError` traceback, no `pairaxis:` prefix, rc=1.

### 4. Misleading exit zero; no ingest of non-files

`n_diff` 0, 1, 2, 4: all rc=0. Fine as a printer; hostile as a pipe predicate. Missing / directory / device / FIFO / process substitution: rc=2 `file not found` even when the bytes are on the fd (`/dev/fd/12`). stdin is not a path. The tool only opens regular files the caller already wrote.

---

## Primitive

Reality-stripped operation: parse two caller-supplied key/value traces, `ast.literal_eval` each value, print the size of the key-union inequality and either the first key or the word `multiple`.

Nearest ordinary workflow: `diff` / `comm` of those files, or reading the analog which already printed `only_axis`. Observable capability lost if pairaxis vanishes: a label `n_diff` / `only_axis` on a dict-diff. That is not a pair runner, not a poetry extras solver, not an order-leak tracer.

That is why this is KILL, not MUTATE. The *question* (which single field of two paired runs explains pass vs fail) is a real debugging object. This embodiment does not ask it of a run. It asks it of traces the caller already extracted. Growing a pytest / poetry / django executor to “see” the pair would be a new harvest, not a patch of this 73-line diff. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First KEEP is not protection. Honor the leftover in `MUTATE.md`: the primitive is already the thin dict-diff.

Do not merge this join onto `main`. Do not grow a solver. Archive left under `lineages/candidate-pairaxis/`. Reimpl of this primitive is not a survivor.

---

KILL
