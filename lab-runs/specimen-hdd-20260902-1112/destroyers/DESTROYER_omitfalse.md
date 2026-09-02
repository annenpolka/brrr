# DESTROYER omitfalse

Date: 2026-09-02 14:01 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-omitfalse/omitfalse`

sha256 `58921da11cf068470e430b674362bf87c015aa2a1e047906ae5dd7cc07e79172` (2848 bytes). No `omitfalse` worktree. Same-trial sibling `lineages/candidate-falseomit/falseomit` exists and is a different embodiment; this record attacks the `omitfalse` archive only.

Origin claim (`CANDIDATE.md` / harvest `hdd-omitfalse`): name which JSON encoding omitted a false key vs kept it, and what missing means downstream. Kind: USEFUL_COMPOSITION. Owned encodings: A `{"name":"x"}` omits `flag`; B `{"flag":false,"name":"x"}` keeps it; downstream treats missing as true. Rejected: invented `cli inspect/diff/probe`.

Happy path is real. Unit tests 3/3 pass (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.083s` `OK`, rc=0). `demo.sh` twice, `demo-1.log` / `demo-2.log` byte-identical (cmp rc=0). That is not enough.

This candidate is a **THIN_WRAPPER** of `key in a` vs `key in b` plus an echo of `--missing-as`. `inspect()` never uses the kept value, never infers a downstream value, never checks that the omitted key was false. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-omitfalse/omitfalse
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-omitfalse/fixtures
```

No merge onto `main`. Parent tree stays coordinator-only. Do not fold this printer into the sibling `falseomit` lineage as a “fix”.

---

## What still works

Owned pair and unseen `debug` pair, and any other two top-level JSON objects, **when the question is only presence of `--key`**.

```bash
python3 "$CLI" "$FIX/a.json" "$FIX/b.json" --key flag
echo rc=$?
```

```text
key	flag
a_has	no
a_value	missing
b_has	yes
b_value	false
omitted	a
downstream_missing	true
disagree	yes
rc=0
```

Unseen `debug`: `omitted	a`, `b_value	false`, rc=0. Reconstructed host `two_encoders.py` (`enc_a` drops `v is not False`, `enc_b` keeps) writes the same two objects; omitfalse on those files is the same TSV, rc=0.

Symlink, FIFO (writer after reader), process substitution, filename with a space, CRLF, Unicode key `フラグ`: rc=0. 10000-key object (~159kB) and 50k-key object (~814kB): presence still rc=0 in ~0.03s. Missing path / directory / empty file / `/dev/null` / invalid UTF-8 / binary / trailing comma / JS comment / NDJSON extra data: `omitfalse: …` rc=1. No args / one arg: argparse rc=2.

That is the whole useful surface. It is also what `key in json.loads(a)` already does.

---

## Implementation

`inspect()` in full:

```python
l_has = key in left
r_has = key in right
omitted = []
if not l_has and r_has:
    omitted.append("a")
if l_has and not r_has:
    omitted.append("b")
if not l_has and not r_has:
    omitted.append("both")
return {
    "key": key,
    "a_has": l_has,
    "a_value": left.get(key, "missing"),
    "b_has": r_has,
    "b_value": right.get(key, "missing"),
    "omitted": omitted,
    "downstream_missing": missing_as,
    "disagree": l_has != r_has,
}
```

`missing_as` is copied into the report. Nothing reads `left[key]` or `right[key]` except to print them. `disagree` is presence XOR.

### 1. THIN_WRAPPER: `key in a` vs `key in b` is the product

Host replica of `inspect` + `format_report` on the owned pair is byte-identical to the CLI (`wrapper == cli: True`):

```text
key	flag
a_has	no
a_value	missing
b_has	yes
b_value	false
omitted	a
downstream_missing	true
disagree	yes
```

Nearest ordinary workflow, host-executed:

```bash
python3 -c 'import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); k="flag"
print("a_has", k in a); print("b_has", k in b)' "$FIX/a.json" "$FIX/b.json"
echo py_rc=$?
```

```text
a_has False
b_has True
py_rc=0
```

```bash
jq -r 'has("flag")' "$FIX/a.json"; echo A_rc=$?
jq -r 'has("flag")' "$FIX/b.json"; echo B_rc=$?
jq -c '{has: has("flag"), flag: .flag}' "$FIX/a.json"
jq -c '{has: has("flag"), flag: .flag}' "$FIX/b.json"
```

```text
false
A_rc=0
true
B_rc=0
{"has":false,"flag":null}
{"has":true,"flag":false}
```

`jq has("flag")` already names presence. `jq .flag` on A is JSON `null` (missing), on B is `false`. two_encoders.py already prints `A_has_flag False` / `B_has_flag True`. omitfalse reprints that as TSV and pastes `downstream_missing	true` next to it. The harvest said printing both encodings still leaves missing-as-true as a hand join. The CLI still leaves that join as two columns.

### 2. Both omit

A `{"name":"x"}` B `{"name":"y"}` `--key flag`:

```text
key	flag
a_has	no
a_value	missing
b_has	no
b_value	missing
omitted	both
downstream_missing	true
disagree	no
rc=0
```

Empty objects `{}` `{}`: same `omitted	both`, `disagree	no`, rc=0. Presence agrees on absence. Downstream of both would infer true if missing-as-true, and both would invert an original false. The CLI does not say that. `disagree	no` reads as “no problem”.

### 3. Neither omit

Both `{"flag":false,"name":"x"}`:

```text
a_has	yes
a_value	false
b_has	yes
b_value	false
omitted	none
downstream_missing	true
disagree	no
rc=0
```

Both `{"flag":true}`: `a_value	true` / `b_value	true` / `omitted	none` / `disagree	no` / rc=0. `downstream_missing	true` is still printed when nothing is missing. The column is not “what missing means for this pair”. It is the default flag.

### 4. Key present true vs false: `disagree	no`

A `{"flag":true,"name":"x"}` B `{"flag":false,"name":"x"}`:

```text
a_has	yes
a_value	true
b_has	yes
b_value	false
omitted	none
downstream_missing	true
disagree	no
rc=0
```

A false B true: same `omitted	none`, `disagree	no`, rc=0. Values disagree. Presence agrees. The primitive is presence-only. JSON string `"false"` vs boolean `false`: `a_value	"false"` / `b_value	false` / `omitted	none` / `disagree	no` / rc=0. Number `0` vs `false`: `a_value	0` / `b_value	false` / `disagree	no` / rc=0.

### 5. Omitting true is labeled the same as omitting false

A `{"name":"x"}` B `{"flag":true,"name":"x"}`:

```text
a_has	no
a_value	missing
b_has	yes
b_value	true
omitted	a
downstream_missing	true
disagree	yes
rc=0
```

Same `omitted	a` as the owned false case. A omit B `null` / `0` / `""`: all `omitted	a`, `disagree	yes`, rc=0. Nested `{"outer":{"flag":false}}` vs `{"flag":false}` `--key flag`: A is “omitted” because the walk is top-level `key in dict`. `--key outer.flag`: `omitted	both`, `disagree	no` (no dotted path). Flag living inside `{"items":[{"flag":false}]}`: `omitted	a` vs B’s top-level false.

The name is omit**false**. The code is omit-any-key.

### 6. `--missing-as` is a caller label, never applied

Owned pair, `--missing-as false`:

```text
omitted	a
downstream_missing	false
disagree	yes
rc=0
```

`--missing-as null` → `downstream_missing	null`. `--missing-as 0` → `0`. `--missing-as inverted` → `inverted`. `--missing-as ''` → empty field (`downstream_missing	` then newline). Both-omit plus `--missing-as false`: `omitted	both` / `downstream_missing	false` / `disagree	no`. No `a_downstream`. No polarity. Changing the flag never changes `omitted` or `disagree`. Same pattern as a CLI that prints `--de` / `--ser` the caller already typed.

### 7. Arrays are not objects (honest refuse)

```text
[1,2,3] vs object     omitfalse: …/arr.json: expected a JSON object   rc=1
object vs array       same, rc=1
array vs array        same, rc=1
[{"flag":false}]      same, rc=1
null / false / true / 0 / "flag" roots   expected a JSON object   rc=1
```

Clean. Not a save. The harvest encodings are objects; arrays are out of scope and the tool says so.

### 8. Duplicate keys: `json.loads` last-wins, silent rc=0

`{"flag":true,"flag":false,"name":"x"}` vs keep-false:

```text
a_has	yes
a_value	false
b_has	yes
b_value	false
omitted	none
disagree	no
rc=0
```

Host `object_pairs_hook` sees pairs `[('flag', True), ('flag', False), ('name', 'x')]`. Last-wins is False, so the duplicate looks like agreement. Reverse `{"flag":false,"flag":true}` vs keep-false: `a_value	true` / `b_value	false` / `omitted	none` / `disagree	no` / rc=0. First false is gone. Duplicate vs omit: last-wins false vs missing → `omitted	b`, as if A kept a single false.

### 9. Stdin

```text
python3 "$CLI" - "$FIX/b.json" --key flag
omitfalse: [Errno 2] No such file or directory: '-'
rc=1
```

Second `-`: same ENOENT rc=1. `/dev/stdin` as first with A redirected: rc=0 (one file can be stdin). `/dev/stdin` `/dev/stdin` with one object on the pipe:

```text
omitfalse: Expecting value: line 1 column 1 (char 0)
rc=1
```

First open consumes the pipe; second is empty. JSON decode errors do not name which of the two paths failed. Decode of invalid UTF-8 / BOM same: `omitfalse: Unexpected UTF-8 BOM …` / `'utf-8' codec can't decode byte 0xff …` rc=1, no filename.

### 10. Huge JSON

10000-key B with `flag: false`, A omit: same 105-byte owned TSV, elapsed 0.028s, rc=0. 50k keys, flag absent in both: `omitted	both`, rc=0, 0.032s. 2MB string in unused key `blob`, query `flag`: still 105 bytes, 0.029s, rc=0. Query `--key blob`: stdout **2000102** bytes, `b_value` is a quoted 2e6 `H` dump, rc=0, no cap. Fine as a printer; hostile as a pipe component.

### 11. Misleading exit zero; TSV holes

`disagree yes`, `omitted both`, true-vs-false, omit-true, duplicate last-wins: all rc=0. No `--check`. Fine as a printer; hostile as a predicate.

`fmt_val` treats JSON string `"missing"` as the absent sentinel (`if value == "missing": return "missing"`). Present `"missing"` vs false:

```text
a_has	yes
a_value	missing
b_has	yes
b_value	false
omitted	none
disagree	no
rc=0
```

`a_has` still distinguishes; `a_value` does not. Tab inside `--key` (`fl\tag`) splits the `key` row (`key	fl	ag`). Empty `--key` on objects without `""`: `omitted	both`, `key	` empty field, rc=0. Empty JSON key `"": false` vs omit with `--key ''`: `omitted	b`, rc=0.

UTF-8 BOM is refused (rc=1). Tests never hit both-omit, true-vs-false, `--missing-as`, arrays, duplicates, stdin, or huge values. Three tests: owned, unseen copy of owned, `/dev/null`.

---

## Primitive

Reality-stripped operation: `json.loads` two files; `key in left`; `key in right`; print TSV; echo `--missing-as` (default `"true"`).

Nearest ordinary workflow: `python3 -c 'print(k in a, k in b)'` or `jq 'has("flag")'` on each encoding, or the owned `two_encoders.py` which already prints `A_has_flag` / `B_has_flag`. Observable capability lost if omitfalse vanishes: **none**. The two JSON objects already are the input. Presence is `in`. Missing-as-true is still a hand join after the TSV.

That is why this is KILL, not MUTATE. The *question* (this encoder omitted a false, missing infers true, polarity inverts) is a real debugging object. This embodiment does not ask it. It asks `key in a` vs `key in b`. Adding `a_downstream` / polarity would be implementing the composition this artifact failed to embody — a new harvest, not a patch of `key in`. Sibling `falseomit` at least restricts `dropped_false` to `k not in A and B[k] is False`; it is a different CLI and a different destroyer. Do not mutate omitfalse into that name to escape THIN_WRAPPER.

Hardcoded ceiling:

- `omitted` = presence gap, including omit-true / omit-null / omit-0 / nested-invisible
- `disagree` = presence XOR, so true-vs-false is `disagree	no`
- `downstream_missing` = argv string, including when nothing is missing
- duplicate keys last-wins
- `-` is not stdin; two `/dev/stdin` is empty-second JSON
- 2MB queried value dumps
- always rc=0 on a split
- Dreamer `inspect/diff/probe` was rejected; this is that inspect, reduced to `key in`

Honor KILL. Dreamer ancestry is not protection.

Do not merge onto `main`.

---

KILL
