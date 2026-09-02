# DESTROYER keyorder 2

Date: 2026-09-02 15:48 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0386
Worker: destroyer-keyorder-2

Target (archive; MUTATE leftover, bytes unchanged):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keyorder/keyorder`

sha256 `21ef57dbd48b531b7b696bb01e7078f12540f1391276d068855a8ca7eede9994` (8456 bytes, 273 lines). Same digest as `DESTROYER_keyorder.md`. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-keyorder-keyorder/keyorder/keyorder` is byte-identical (`cmp` rc=0). HEAD `f5213929acb59a4b327cc9c92fe204ad5112ec2b` (`Record keyorder empirical transcript from owned-fixture demos.`), branch `specimen-hdd/candidate-keyorder-keyorder`. Parent `main` is `432f954`; `git ls-tree HEAD keyorder` empty. Host Python 3.14.5. unittest 15/15 OK, 0.364s. `demo-1.log` / `demo-2.log` byte-identical. No `MUTATE.md`. No Hypothesis, no pytest dump scrape, no pretty-printer port, no `json` import. Not merged onto `main`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-hypothesis` / specimen-034): label each displayed mapping as sorted-keys vs insertion-order when those views disagree, and name the printer that reordered keys. Kind: USEFUL_COMPOSITION. Research boundary: no Hypothesis checkout, no pytest dump scraping, no vendor pretty-printer port.

First destroyer (`DESTROYER_keyorder.md`) **MUTATE**: owned `{1: 0, 0: 0}` pair is real; `insertion-order` without `--obj` means "not sorted"; `disagree` skips `--obj`; `list(d)` refused; nested values traceback; `reordered none` beside a real split. Kill leftover: if mutation cannot do (1) stop lying about insertion-order (2) `disagree` includes the object (3) accept key sequences, a later destroyer should KILL. Those three did not land. Bytes unchanged. First MUTATE is not protection.

This candidate is a **THIN_WRAPPER of key-order diff on caller JSON / mapping literals**: `tuple(keys)` vs `tuple(sorted(keys))` vs `tuple(--obj)` after `ast.literal_eval` of texts the caller already isolated. Independent replica of that comparison (no import of the CLI) is **byte-identical** to CLI stdout+rc on **29/29** host cases, including JSON objects. `json.loads` + `list(d)==sorted(d)` vs `list(d)==list(obj)` matches CLI labels **4/4**. `jq keys` vs `keys_unsorted` already names the JSON split. `demo.sh` already prints `print(d)` / `list(d)` / `sorted(d)` before invoking the CLI. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keyorder/keyorder
FX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keyorder/fixtures
S034=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-034
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not grow a pytest dump parser, a pretty-printer port, or a nested-order walker to escape THIN_WRAPPER. Do not send key-order theater back to R1. Do not wrap `json.dumps(..., sort_keys=True)`.

---

## What still works

Owned `{1: 0, 0: 0}` and any other case where the caller already extracted one-line mapping / JSON object texts and, for JSON, already chose string keys.

```bash
python3 "$CLI" --fixture; echo rc=$?
```

```text
obj	{1: 0, 0: 0}
obj_keys	1	0
sorted_keys	0	1
display	pretty	{0: 0, 1: 0}	sorted-keys
display	repr	{1: 0, 0: 0}	insertion-order
same_items	yes
disagree	yes
reordered	pretty
faithful	repr
rc=0
```

`--file "$FX/three_views.txt"`: `reordered	pytest	falsifying`, `faithful	note`. Caller JSON `{"b": 1, "a": 0}` vs `json.dumps(..., sort_keys=True)`: `reordered	0`, `faithful	1`. unittest 15/15. Missing file rc=1. `not-a-dict` rc=2.

That is the first MUTATE's "what still works". It is also `list(d)==sorted(d)` vs `list(d)==list(obj)` on argv the caller already typed. Printer names are caller-supplied (`pretty	`, `--fixture` hardcodes them, positionals are `0`/`1`).

---

## Implementation

Load-bearing body:

```python
def classify(mapping, obj):
    keys = tuple(mapping)
    sk = tuple(sorted(mapping))          # TypeError → unsortable
    is_sorted = keys == sk
    if obj is None:
        return "sorted-keys" if is_sorted else "insertion-order"
    if is_sorted:
        return "sorted-keys"
    if keys == tuple(obj):
        return "insertion-order"
    return "other"

# inspect:
#   disagree = len(set(tuple(m) for m in displays)) > 1   # --obj not in the set
#   reordered = names whose keys == sorted(obj) and keys != obj_keys
#   faithful  = names whose keys == obj_keys
# parse_mapping: ast.literal_eval after ASCII NAME = { strip
```

`classify.co_names` is `('tuple', 'sorted_key_tuple')`. `inspect.co_names` is `('append', 'format_mapping', 'sorted_key_tuple', 'classify', 'frozenset', 'items', 'TypeError', 'all', 'bool', 'tuple', 'len', 'set', 'list', 'dict', 'fromkeys')`. `sorted_key_tuple.co_names` is `('tuple', 'sorted', 'TypeError')`. `parse_mapping.co_names` is `('strip_display_prefix', 'ValueError', 'ast', 'literal_eval', 'SyntaxError', 'isinstance', 'dict')`. Source contains no `json`, no Hypothesis, no pytest runner, no `pprint`. `--fixture` hardcodes `OWNED_OBJ = {1: 0, 0: 0}`.

`main` returns 0 after a successful parse. `disagree yes` is still rc=0.

---

## 1. THIN_WRAPPER of key-order diff on caller JSON

Independent reconstruction of `classify` + `inspect` TSV (no import) is **byte-identical** to CLI stdout+rc on **29/29** host cases: `--fixture`, `two_prints.txt`, `two_prints_obj.txt`, `agree.txt`, `three_views.txt`, positional owned, infer without `--obj`, spacing, `d=` prefixes, different items, one sorted vs `--obj`, two unsorted permutations, `other` permutation, wrong sorted `--obj`, lone unsorted, JSON string-key pair, JSON already-sorted obj, JSON three permutations, `json.dumps` / `sort_keys=True` pair, `True` vs `1`, `1.0` vs `1`, `False`+`0` collapse, tuple keys, bytes keys, unicode keys, numeric-string keys, empty dicts, single key, three-int pprint pair.

Load-bearing JSON analog (host-executed, no CLI import):

```bash
python3 -c '
import json
obj = json.loads("{\"b\": 1, \"a\": 0}")
for s in ["{\"a\": 0, \"b\": 1}", "{\"b\": 1, \"a\": 0}"]:
    d = json.loads(s)
    print(list(d),
          "sorted-keys" if list(d)==sorted(d) else
          ("insertion-order" if list(d)==list(obj) else "other"))
'
python3 "$CLI" --obj '{"b": 1, "a": 0}' '{"a": 0, "b": 1}' '{"b": 1, "a": 0}'
```

```text
['a', 'b'] sorted-keys
['b', 'a'] insertion-order

obj	{'b': 1, 'a': 0}
obj_keys	'b'	'a'
sorted_keys	'a'	'b'
display	0	{'a': 0, 'b': 1}	sorted-keys
display	1	{'b': 1, 'a': 0}	insertion-order
same_items	yes
disagree	yes
reordered	0
faithful	1
rc=0
```

`json.loads` labels match CLI display labels **4/4** (`json_string_keys`, `json.dumps` pair, already-sorted JSON, JSON three-perm insertion vs sorted). Replica stdout on those JSON cases is byte-identical to the CLI.

Nearest ordinary workflow on caller JSON, also host-executed:

```bash
python3 -c 'import json; d={"b":1,"a":0}
print(json.dumps(d))
print(json.dumps(d, sort_keys=True))'
printf '%s\n' '{"b":1,"a":0}' | jq -r 'keys_unsorted | join(" ")'
printf '%s\n' '{"b":1,"a":0}' | jq -r 'keys | join(" ")'
```

```text
{"b": 1, "a": 0}
{"a": 0, "b": 1}
b a
a b
```

`jq keys` sorts. `jq keys_unsorted` preserves insertion. `json.dumps(..., sort_keys=True)` is the sorted text. The CLI reprints those two key tuples as `sorted-keys` / `insertion-order` and pastes caller names into `reordered` / `faithful`. The harvest said the miss is naming which printer reordered keys. The printers are argv. The names are argv.

Owned Python pair, `demo.sh` already prints the analog before the CLI:

```text
== nearest existing operation: print(d) vs print(list(d)) vs sorted(d) ==
print(d) {1: 0, 0: 0}
list(d) [1, 0]
sorted(d) [0, 1]
```

```bash
python3 -c "
import ast
obj = ast.literal_eval('{1: 0, 0: 0}')
for s in ['{0: 0, 1: 0}', '{1: 0, 0: 0}']:
    d = ast.literal_eval(s)
    print(list(d), 'sorted' if list(d)==sorted(d) else 'not-sorted',
          'matches_obj' if list(d)==list(obj) else 'differs')
"
```

```text
[0, 1] sorted differs
[1, 0] not-sorted matches_obj
```

That one-liner is `classify`. The TSV is formatting. `--fixture` is the specimen hardcoded.

README: "Mapping literals only (not JSON, not `list(d)`)." Real JSON `true` / `null` is refused (`ast.literal_eval`, not `json.loads`):

```bash
python3 "$CLI" --obj '{"ok": true}' '{"ok": true}'
# keyorder: not a mapping literal: '{"ok": true}'
# rc=2
python3 "$CLI" '{"a": null}'
# keyorder: not a mapping literal: '{"a": null}'
# rc=2
```

The CLI is not a JSON parser. When the caller supplies JSON objects whose tokens are also Python literals (string keys, numeric values), `json.loads` key-order **is** the CLI. That is the THIN_WRAPPER.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`obj_keys`, `sorted_keys`, `same_items`) to escape classification. Those rows are `tuple(obj)` / `tuple(sorted(obj))` / `frozenset(items)`. They do not vote beyond the one-liner.

---

## 2. First MUTATE leftover: (1)+(2)+(3) never landed

No `MUTATE.md`. sha256 unchanged from the first destroyer. The three kill-condition items:

**(1) Stop lying about insertion-order.** Without `--obj`, unsorted is still `insertion-order`. Two unsorted permutations still both get that label. A lone `{1: 0, 0: 0}` is still `insertion-order`, `reordered	none`, `faithful	0`.

```bash
python3 "$CLI" '{2: 0, 0: 0, 1: 0}' '{1: 0, 0: 0, 2: 0}' '{0: 0, 1: 0, 2: 0}'
```

```text
display	0	{2: 0, 0: 0, 1: 0}	insertion-order
display	1	{1: 0, 0: 0, 2: 0}	insertion-order
display	2	{0: 0, 1: 0, 2: 0}	sorted-keys
disagree	yes
rc=0
```

No `reordered`/`faithful` rows (infer refuses two unsorted tuples). Replica identical.

**(2) `disagree` includes the object.** One sorted display vs insertion `--obj`:

```bash
python3 "$CLI" --obj '{1: 0, 0: 0}' '{0: 0, 1: 0}'
```

```text
display	0	{0: 0, 1: 0}	sorted-keys
disagree	no
reordered	0
faithful	none
rc=0
```

The printer reordered. `reordered` says so. `disagree` says no. `--obj` is still not in `set(orders)`. Replica identical.

`reordered none` next to a real split (`other` dropped) still holds:

```bash
python3 "$CLI" --obj '{1: 0, 0: 0, 2: 0}' '{2: 0, 1: 0, 0: 0}' '{1: 0, 0: 0, 2: 0}'
```

```text
display	0	{2: 0, 1: 0, 0: 0}	other
display	1	{1: 0, 0: 0, 2: 0}	insertion-order
disagree	yes
reordered	none
faithful	1
rc=0
```

**(3) Accept key sequences.** Specimen-034 insertion evidence is `assert [0, 1] == [1, 0]`.

```bash
python3 "$CLI" --obj '{1: 0, 0: 0}' '[1, 0]' '{0: 0, 1: 0}'
# keyorder: not a mapping: '[1, 0]'
# rc=2
```

`--file` of the origin dump blob (`OBSERVED.md`) dies on the first non-literal line, rc=2. Nested values still traceback at `frozenset(m.items())`, rc=1, no `keyorder:` prefix. List values same.

First MUTATE said: if (1)+(2)+(3) cannot land, the object is still `list(d)==sorted(d)` with extra print, and a later destroyer should KILL. This is that later destroyer. Bytes never moved.

---

## 3. Caller already extracted the texts; names are argv

`three_views.txt` is three mapping lines a human cut out of the pytest/Hypothesis dump and labeled `pytest` / `note` / `falsifying`. That extraction **is** the join the harvest promised. The CLI labels the key tuples.

`--fixture` does not observe printers. It formats `OWNED_OBJ` twice (`sorted(keys)` vs insertion) and names them `pretty` / `repr`.

JSON `json.dumps(d)` vs `json.dumps(d, sort_keys=True)` is the same observation without Hypothesis. After pasting both literals, keyorder names display `0` as `sorted-keys` / `reordered`. Transfer is real and is **stdlib json**, not a new object. It still requires the caller to already have both texts.

`True` vs `1`, `1.0` vs `1`, `{False: 1, 0: 2}` collapsing to `{False: 2}`: identity is Python `==` after `literal_eval`, not displayed key text. Replica identical. First MUTATE item 7 never landed.

Empty `--file /dev/null`: `need a mapping display, --file, or --fixture`, rc=2. `--file` was given. First MUTATE item 6 never landed.

Always rc=0 on a split. No `--check`. Fine as a printer of `tuple(keys)==tuple(sorted(keys))`; hostile as a pipe predicate.

15 tests never hit unhashable values, `other`, disagree-vs-obj, JSON `true`, dumps, or rc-on-split.

---

## Primitive

Reality-stripped operation: `ast.literal_eval` each caller mapping / JSON-shaped object text; compare `tuple(keys)` to `tuple(sorted(keys))` and to `tuple(--obj)`; print TSV labels; exit 0 if the texts parsed.

Nearest ordinary workflow (owned packet, also `demo.sh`, also specimen-034 `list(d)` vs `sorted(d)`, also `json.dumps(sort_keys=True)`, also `jq keys` / `keys_unsorted`):

```text
python3 -c 'print(list(d)==sorted(d), list(d)==list(obj))'
json.dumps(d, sort_keys=True) vs json.dumps(d)
jq -r 'keys | join(" ")' vs jq -r 'keys_unsorted | join(" ")'
```

On specimen-034 that pair is: pretty-printer sorted keys, object insertion was `[1, 0]`, copying the Falsifying example does not fail. keyorder’s load-bearing claim is that naming `reordered pretty` is a join those two mapping texts plus `sorted(d)` do not already contain.

It is not. The texts are the input. Sorted-vs-insertion is `list(d)==sorted(d)` vs `list(d)==list(obj)`. Printer names are argv. Wrapping Hypothesis `pretty._dict_pprinter_factory` or scraping a pytest dump to recover `list(d)` would be a new harvest (out of research boundary, and out of the bytes that exist). First MUTATE asked for key sequences and dump skip; they never landed. Do not grow them now to escape THIN_WRAPPER. Do not send this back to R1 with “make this more novel.”

That is why this is KILL, not a second MUTATE. The *question* (which displayed form of this mapping sorted keys, which preserved insertion, when they disagree) is a real debugging object. This embodiment does not ask it of printers. It asks it of mapping / JSON literals the caller already isolated. Adding dump extraction / `list(d)` / nested order would be implementing the composition this artifact failed to embody — a new harvest, not a patch of `tuple==sorted`. First-destroyer MUTATE is not protection once that leftover is shown to be labels on a key-order diff of caller JSON.

Hardcoded ceiling:

- `sorted-keys` ↔ `tuple(keys)==tuple(sorted(keys))`
- `insertion-order` ↔ `tuple(keys)==tuple(obj)`, or without `--obj` every unsorted permutation
- `other` ↔ neither; then omitted from `reordered` (`reordered none` beside `disagree yes`)
- `disagree` ↔ display key-tuples differ; `--obj` is a spectator
- `reordered` ↔ sorted and not insertion; reverse / arbitrary permutation unnamed
- `faithful` ↔ matches `--obj` (or the unique unsorted display)
- `same_items` ↔ `frozenset(items)`; nested/list values traceback
- mapping literals only; JSON `true`/`null` rc=2; `list(d)` rc=2; dump blob rc=2
- `--fixture` is `{1: 0, 0: 0}` hardcoded
- printer names are caller-supplied
- always rc=0 on a split
- no Hypothesis, no pytest, no pretty port, no `json.loads`

Honor KILL. Dreamer ancestry is not protection. First MUTATE is not protection. Kill leftover `(1)+(2)+(3)` holds. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Constitution: a THIN_WRAPPER does not gain a dump parser or a pretty-printer to escape classification.

Do not merge onto `main`. Do not wrap `json.dumps(sort_keys=True)` or `jq keys`. Archive stays under `lineages/candidate-keyorder/`. Worktree stays under `~/.grok/worktrees/annenpolka-brrr/candidate-keyorder-keyorder/`.

KILL
