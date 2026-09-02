# DESTROYER falseomit 2

Date: 2026-09-02 15:35 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive, KEEP survivor):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-falseomit/falseomit`

CLI sha256 `b7e6adbf6daccf5152be5f95fa39775cb717030a51c7055123764c238022e6eb` (3279 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-falseomit-falseomit/falseomit/falseomit` is byte-identical (`cmp` rc=0; branch `specimen-hdd/candidate-falseomit-falseomit`, HEAD `9e7a397 ground falseomit from hdd-omitfalse harvest`). Parent `main` is `432f954`; `falseomit` is not in that tree. Tests: `python3 -m unittest discover -s …/tests -v` → 6/6 OK, 0.134s, rc=0. `demo.sh` twice to temp logs: byte-identical, matches archived `demo-1.log` / `demo-2.log`. Host Python 3.14.5. jq and go on PATH; go was used only to mint omitempty encodings, not as a product. No merge onto `main`.

Origin: specimen-077 / hdd-omitfalse. Two encodings of `{flag: false, name: x}`: encoder A omits `flag` because it is false (`json.dumps` skip-False / Go `json:",omitempty"`); encoder B keeps `"flag": false`. Downstream treats missing as true. Classification: USEFUL_COMPOSITION. Primitive claimed: name keys present as false in one JSON encoding and absent in the other (missing decoded as true). First destroyer (`DESTROYER_falseomit.md`) KEEP: owned `dropped_false flag`, unseen `enabled`, same object `none`, swap A/B `none` (directional), missing file rc=1, tests 6/6. First KEEP is not protection. Sibling `omitfalse` was Honor-KILLed (`DESTROYER_omitfalse.md`, fossil `fossils/omitfalse.md`) as THIN_WRAPPER of `key in a` vs `key in b` plus echo of `--missing-as`. This is that second pass.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-falseomit/falseomit
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-falseomit/fixtures
ENC=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-077/files/two_encoders.py
OMIT=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-omitfalse/omitfalse
```

Host-executed against the archive only. Worktree was not edited. This candidate is a **THIN_WRAPPER of json omit-false vs include-false on caller JSON**: `dropped_false = [k for k, v in B.items() if k not in A and v is False]`. Independent reconstruction of full stdout is IDENTICAL 29/29. The same one-liner matches `dropped_false` 29/29. `a_has` / `b_has` / `b_value` are tautologies of that filter. `missing_decoded_as` is the literal `true`, never applied. Decision: **KILL**.

---

## What still works

Owned A vs B, unseen `enabled`, same object, swap, missing path, empty file, `/dev/null`, directory, no args. stdin `-` / `/dev/stdin` / FIFO / process substitution / symlink / filename with a space / CRLF / Unicode key: harvest. That is the first KEEP. It is also `k not in A and B[k] is False` on two objects the caller already wrote.

```bash
python3 "$CLI" "$FIX/a.json" "$FIX/b.json"
echo rc=$?
```

```text
keys_a	name
keys_b	flag	name
missing_in_a	flag
missing_in_b	none
false_in_a	none
false_in_b	flag
dropped_false	flag
missing_decoded_as	true
a_has	flag	no
b_has	flag	yes
b_value	flag	false
rc=0
```

Unseen `enabled`: `dropped_false	enabled`, rc=0. Same B/B: `dropped_false	none`, rc=0, no `a_has` rows. Swap (false present in A, absent in B): `dropped_false	none`, `missing_in_b	flag`, `false_in_a	flag`, rc=0. Missing `/no/such/a.json`: empty stdout, `falseomit: [Errno 2] No such file or directory: '/no/such/a.json'`, rc=1. `/dev/null`: `invalid JSON: Expecting value`, rc=1. Directory: `Is a directory`, rc=1. No args / one arg: argparse rc=2. `--help` rc=0.

Sibling Honor-killed `omitfalse` on the same owned pair prints `omitted	a` / `b_value	false` / `downstream_missing	true` / `disagree	yes`, also rc=0. Same question, same caller JSON, different TSV labels.

That is the whole useful surface. Attacks below show `dropped_false` does not join missing-as-true, does not walk nested flags, and does not care which encoder produced the files.

---

## Implementation

Load-bearing body of `inspect()`:

```python
dropped_false = [k for k in missing_in_a if second.get(k) is False]
```

which is:

```python
dropped_false = [k for k, v in second.items() if k not in first and v is False]
```

`inspect.co_names` is `('list', 'items', 'get')`. The rest of the dict is labels:

- `keys_a` / `keys_b` = `list(dict)`
- `missing_in_a` / `missing_in_b` = key set-difference
- `false_in_a` / `false_in_b` = `v is False`
- `a_has` = `{k: k in first for k in dropped_false}` → always False
- `b_has` = `{k: k in second for k in dropped_false}` → always True
- `b_value` = `{k: second.get(k) for k in dropped_false}` → always False

`format_report` then appends the literal `missing_decoded_as	true`. That string is not an argument, not read from either object, and never used to compute a downstream value. `inspect()` does not contain it.

`demo.sh` already names the nearest operation: `json.dumps + key membership` / `A {"name": "x"}  flag not in object` / `B {"flag": false, "name": "x"}  flag present false`.

### 1. THIN_WRAPPER of omit-false vs include-false on caller JSON

Independent reconstruction of `inspect()` + `format_report` (no import of the CLI as a package; host copy of the six list comps plus the hardcoded MDA line) is **byte-identical** to CLI stdout on **29/29** host cases: owned, unseen, same-B, swap, both-omit, empty-empty, both-keep-false, true-vs-false, false-vs-true, omit-true, omit-null, omit-0, omit-empty-str, omit-empty-list, string-false-vs-bool-false, 0-vs-false, nested-vs-top, nested-both, A-false-B-other-false, multi-dropped, extra-true-missing, A-extra-false, unicode-key, empty-key-false, json-string `"missing"`, present-null-vs-false, list-value-false-inside, both-true, A-omit-B-false.

The load-bearing column without the spectator lists:

```bash
python3 -c 'import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2]))
print("dropped", "\t".join(k for k,v in b.items() if k not in a and v is False) or "none")
print("a_has_flag", "flag" in a); print("b_has_flag", "flag" in b)
print("b_flag", b.get("flag", "missing"))' "$FIX/a.json" "$FIX/b.json"
echo py_rc=$?
```

```text
dropped flag
a_has_flag False
b_has_flag True
b_flag False
py_rc=0
```

Host `dropped` equals CLI `dropped_false` on 29/29. `a_has_flag` / `b_has_flag` are what `two_encoders.py` already prints (`A_has_flag False` / `B_has_flag True`).

Nearest ordinary workflow, also host-executed:

```bash
jq -n --slurpfile a "$FIX/a.json" --slurpfile b "$FIX/b.json" \
  '$b[0] | to_entries[] | select(.value == false) | .key | select(. as $k | ($a[0] | has($k) | not))'
jq -r 'has("flag")' "$FIX/a.json"; echo A_rc=$?
jq -r 'has("flag")' "$FIX/b.json"; echo B_rc=$?
jq -c '{has: has("flag"), flag: .flag}' "$FIX/a.json"
jq -c '{has: has("flag"), flag: .flag}' "$FIX/b.json"
```

```text
"flag"
false
A_rc=0
true
B_rc=0
{"has":false,"flag":null}
{"has":true,"flag":false}
```

`jq has("flag")` already names presence. `jq select(.value == false)` plus `has|not` already names omit-false vs include-false. `two_encoders.py` already prints the two objects and the two membership bits. falseomit reprints that as TSV and pastes `missing_decoded_as	true` next to it. The harvest said the miss is the join with missing-as-true. The CLI still leaves that join as a constant column.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`keys_a`, `missing_in_*`, `false_in_*`, tautological `a_has`/`b_has`/`b_value`) to escape classification. Those rows are `list` / set-difference / `is False` labels. They do not vote beyond the one-liner.

### 2. `missing_decoded_as` is never applied

Every successful object-pair in the 29-case table prints `missing_decoded_as	true`, including:

- same object, nothing missing
- both omit `flag`
- both keep `flag: false`
- true-vs-false (values disagree, presence agrees)
- omit-true (`missing_in_a	flag`, `dropped_false	none`)
- empty `{}` `{}`

There is no `--missing-as`. There is no `a_downstream`. There is no polarity (original false, decoded true). Changing nothing can change the column: it is a string literal in `format_report`. Same extinction class as sibling omitfalse echoing `--missing-as` / default `"true"` into `downstream_missing` without using it.

Owned pair plus the harvest claim “downstream treats missing as true inverts the omitted false”: the CLI never says the decoded A is `flag=true`. It says `a_has flag no` (true by construction) and `missing_decoded_as true` (true by source).

### 3. Directional filter, not “one encoding vs the other”

Help text: “Name keys present as false in *one* encoding and absent in the other.” Code: only B-has-false and A-absent.

Swap owned (B then A): `dropped_false	none`, rc=0. First KEEP called this “directional by harvest (B kept false, A omitted). Not a kill.” It is not a FIX. It is also not a join. A false that A kept and B omitted is `false_in_a` plus `missing_in_b` and then discarded. `A-extra-false` (`dead: false` only in A): `dropped_false	none`. `A-false-B-other-false`: reports `other`, not `flag`.

### 4. Omit-true / omit-null / omit-0 is not dropped_false; presence disagreement is silent rc=0

A `{"name":"x"}` B `{"flag":true,"name":"x"}`:

```text
missing_in_a	flag
dropped_false	none
missing_decoded_as	true
rc=0
```

Sibling omitfalse on the same files: `omitted	a` / `b_value	true` / `disagree	yes`. falseomit’s False-filter is the only delta vs that killed printer. It still does not apply missing-as-true. Omit-null / omit-0 / omit-`""` / omit-`[]`: same `dropped_false	none`, `missing_in_a	flag`, rc=0.

Both `{"flag":true}`: `dropped_false	none`, `missing_decoded_as	true`, rc=0. True-vs-false both present: `false_in_b	flag`, `dropped_false	none`, rc=0. Values disagree. The primitive is presence-of-False-in-B-not-A.

JSON string `"false"` vs boolean `false`: `dropped_false	none` (key present in A). Number `0` vs `false`: same. Nested `{"outer":{"flag":false}}` vs `{"flag":false}`: `dropped_false	flag` because the walk is top-level `k in dict`. Nested-both: `dropped_false	none` (the inner false is invisible; `false_in_a`/`false_in_b` are `none`). Flag living inside `{"items":[{"flag":false}]}` vs top-level false: `dropped_false	flag`.

### 5. Go `omitempty` and `two_encoders.py` already are the input

Host `go run` of `Flag bool json:"flag,omitempty"` vs `json:"flag"`:

```text
A {"name":"x"}
B {"flag":false,"name":"x"}
```

falseomit on those two files: the owned TSV, `dropped_false	flag`, rc=0. The same python one-liner: `dropped flag` / `a_has_flag False` / `b_has_flag True`, rc=0.

Host `python3 "$ENC"`:

```text
A {"name": "x"}
B {"flag": false, "name": "x"}
A_has_flag False
B_has_flag True
```

falseomit on those objects: the owned TSV again. The specimen *is* the two JSON files. The CLI does not run an encoder, does not read a struct tag, does not decode with missing-as-true. Job input was “SECOND pass omitempty false”. omitempty already happened before argv.

### 6. Arrays / non-objects refuse (honest); tests never hit them

```text
[1,2,3] vs object     falseomit: …: expected a JSON object   rc=1
object vs array       same, rc=1
array vs array        same, rc=1
[{"flag":false}]      same, rc=1
null / false / true / 0 / "flag" roots   expected a JSON object   rc=1
```

Clean. Not a save. `test_not_object` runs `a.json` vs `a.json` (two objects, rc=0). Arrays are untested. Empty file / `/dev/null` / trailing comma / JS comment / NDJSON extra data / bare `not json`: `invalid JSON`, rc=1. UTF-8 BOM: `Unexpected UTF-8 BOM`, rc=1. Invalid UTF-8 / binary: codec error rc=1 (binary names no path).

### 7. Duplicate keys: `json.loads` last-wins, silent rc=0

`{"flag":true,"flag":false,"name":"x"}` vs keep-false: `dropped_false	none` (A last-wins False, key present). Host `object_pairs_hook` sees `[('flag', True), ('flag', False), ('name', 'x')]`. Reverse `{"flag":false,"flag":true}` vs keep-false: `dropped_false	none`, `false_in_a	none` (last-wins True). First false is gone.

### 8. Stdin / pipes

`-` as A with owned omit on stdin: owned TSV, replica True, rc=0. `-` as B: same. Two `-` on one stream: `falseomit: -: invalid JSON: Expecting value: line 1 column 1 (char 0)`, rc=1 (first read consumes the pipe). `/dev/stdin` as A: rc=0. Two `/dev/stdin`: same empty-second JSON, rc=1. FIFO writer-after-open, process substitution, symlink, space in filename, CRLF: owned harvest, rc=0. Sibling omitfalse treated `-` as ENOENT. falseomit’s stdin is honesty, not a primitive.

### 9. Huge JSON; keys_* dump; empty-key TSV hole; always rc=0

10000-key A omit `flag`, B keep: `dropped_false	flag`, rc=0, **117958 bytes** because `keys_a`/`keys_b` dump every name, 0.029s. 50k keys, flag absent in both: `dropped_false	none`, **677905 bytes**, 0.039s. 2MB unused `blob` in B: stdout 198 bytes (key name `blob` in `keys_b`/`missing_in_a`, value not dumped), `dropped_false	flag`, rc=0. Fine as a printer of `list(dict)`; hostile as a pipe component. The load-bearing column is still the one-liner.

Empty JSON key `"": false` vs `{}`:

```text
keys_b	
missing_in_a	
false_in_b	
dropped_false	
a_has		no
b_has		yes
b_value		false
rc=0
```

Tab-split sees empty fields. `dropped_false` is a blank, not `none`.

`dropped_false none`, omit-true, true-vs-false, swap, both-omit, duplicate last-wins: all rc=0. No `--check`. Distinction is the `dropped_false` row, which the one-liner already is.

Unicode key `フラグ`: `dropped_false	フラグ`, tautological `a_has`/`b_has`/`b_value`, rc=0 — still `k not in A and v is False`.

Tests never hit swap, omit-true, both-omit, true-vs-false, `--` anything, arrays, duplicates, stdin, BOM, huge keys, or empty key. Six tests: owned, unseen copy of owned, B vs B, missing path, and a.json vs a.json labeled `test_not_object`.

---

## Primitive

Reality-stripped operation: `json.loads` two caller files; `dropped_false = [k for k,v in B.items() if k not in A and v is False]`; print dict keys, two set-differences, two `is False` lists, that filter, the literal `missing_decoded_as	true`, and three tautological rows per hit; exit 0 if both values were objects.

Nearest ordinary workflow (owned packet, also `demo.sh`, also specimen-077 `two_encoders.py`, also Go `omitempty`):

```text
python3 -c 'print([k for k,v in b.items() if k not in a and v is False])'
jq 'has("flag")' on each encoding
jq select(.value==false) plus has|not
print A_has_flag / B_has_flag
```

On specimen-077 that pair is: A omitted false, B kept false, missing infers true. falseomit’s load-bearing claim is that naming `dropped_false` is a join those two objects plus missing-as-true do not already contain.

It is not. The objects are the input. Presence-of-False-in-B-not-A is `k not in a and v is False`. Missing-as-true is still a hand join after the TSV. Wrapping an encoder / `json.Unmarshal` missing-key-as-true to print polarity would be a new harvest (live codec, out of scope). Sibling `omitfalse` already prints presence of a named `--key` plus an unused `downstream_missing` and was Honor-KILLed for that. Do not mutate falseomit into omitfalse to escape THIN_WRAPPER. Do not send it back to R1 to “make this more novel.”

That is why this is KILL, not MUTATE. The *question* (this encoder omitted a false, missing infers true, polarity inverts) is a real debugging object. This embodiment does not ask it. It asks `k not in A and B[k] is False` on JSON the caller already wrote. Adding `a_downstream` / polarity would be implementing the composition this artifact failed to embody — a new harvest, not a patch of the False-filter. First-destroyer KEEP is not protection once that KEEP is shown to be labels on omit-false vs include-false. Sibling Honor-KILL is the same extinction class with a slightly thinner filter (`key in` vs `key in and v is False`).

Hardcoded ceiling:

- `dropped_false` ↔ `k not in A and B[k] is False` (B-keep / A-omit only)
- `a_has` / `b_has` / `b_value` are tautologies of that filter
- `missing_decoded_as` = the string `true`, including when nothing is missing
- omit-true / omit-null / omit-0 / nested-invisible are not dropped_false
- true-vs-false both present is `dropped_false	none`, rc=0
- swap (A kept false, B omitted) is `dropped_false	none`
- duplicate keys last-wins
- two `-` / two `/dev/stdin` is empty-second JSON
- `keys_a`/`keys_b` dump every name (10k keys → 118kB stdout)
- empty key splits TSV; `dropped_false` blank not `none`
- always rc=0 on a split
- no encoder, no struct tag, no missing-as-true decode
- Dreamer `inspect/diff/probe` was rejected; this is that inspect, reduced to the False-filter

Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection. Do not grow an encoder runner or a missing-as-true decoder to escape THIN_WRAPPER. Do not merge falseomit onto `omitfalse` or onto `main`.

Archive stays under `lineages/candidate-falseomit/`.

KILL
