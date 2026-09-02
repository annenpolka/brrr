# DESTROYER keyorder

Date: 2026-09-02 12:51 JST

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keyorder/keyorder`

sha256 `21ef57dbd48b531b7b696bb01e7078f12540f1391276d068855a8ca7eede9994` (8456 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-keyorder-keyorder/keyorder/keyorder` is byte-identical.

Origin claim (`CANDIDATE.md` / harvest `hdd-hypothesis`): label each displayed mapping as sorted-keys vs insertion-order when those views disagree, and name the printer that reordered keys. Specimen `[specimen-034]`. Kind: USEFUL_COMPOSITION. Research boundary: no Hypothesis checkout, no pytest dump scraping, no vendor pretty-printer port.

Happy path is real. Unit tests (15/15) pass. Owned `{1: 0, 0: 0}` printed with `sorted(keys)` vs insertion is `pretty` `sorted-keys` / `repr` `insertion-order`, `reordered	pretty`. Transcribed three_views of the specimen (`pytest` / `note` / `falsifying`) name the two sorted printers. That is not enough. The `insertion-order` label is `tuple(keys) != tuple(sorted(keys))` unless `--obj` is given; `disagree` ignores `--obj`; `list(d)` — the specimen's actual insertion evidence — is refused; nested values traceback; `reordered none` sits next to a real key-order split.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keyorder/keyorder
FX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keyorder/fixtures
S034=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-034
```

No merge onto `main`. No merge with a pretty-printer port or a pytest scraper. This object is the join on displayed key order, not Hypothesis.

---

## What still works

The owned two-int pair, and any other pair of Python mapping literals with hashable values whose key order is either `sorted(keys)` or the `--obj` insertion tuple.

```bash
python3 "$CLI" --fixture
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

`--file "$FX/three_views.txt"` (prefixed `d =` / `d=` / trailing comma): `reordered	pytest	falsifying`, `faithful	note`. Unique unsorted display infers obj without `--obj`. Spacing `{1:0,0:0}` normalizes. Tuple / bytes / unicode / numeric-string keys classify. `json.dumps(..., sort_keys=True)` vs insertion, and stdlib `pprint.pformat` vs `repr` of `{3: 0, 1: 0, 2: 0}`, both name the sorted text — **if** the caller already extracted one-line mapping literals. `--file -`, `/dev/stdin`, FIFO, symlink, CRLF, space in filename: rc=0. `__import__` / `{**{}}` / `dict([(1,0)])` rejected. `PYTHONHASHSEED` 0/1/random does not shuffle insertion labels.

That is the whole useful delta. Attacks below break the insertion-order claim around it, or show the primitive cannot see the displays the origin specimen actually printed.

---

## Implementation

### 1. Nested / unhashable values are a traceback, not a row

CANDIDATE suggested "Nested mapping value order" as a mutation. Current `inspect` does:

```python
item_sets = [frozenset(m.items()) for _, m in parsed]
```

The `TypeError` guard wraps only `--obj`, not the displays.

```bash
python3 "$CLI" --obj '{1: {0: 1, 1: 0}}' '{1: {1: 0, 0: 1}}' '{1: {0: 1, 1: 0}}'
```

```text
Traceback (most recent call last):
  ...
  File ".../keyorder", line 133, in inspect
    item_sets = [frozenset(m.items()) for _, m in parsed]
TypeError: cannot use 'tuple' as a set element (unhashable type: 'dict')
rc=1
```

Same crash for list values `{1: [0], 0: [1]}` and for two displays of `{1: {2: 0, 0: 0}}` vs `{1: {0: 0, 2: 0}}` (outer keys agree; inner order is the question). No `keyorder:` prefix. Tuple values are hashable and work — the hole is specifically the nested/list shape the mutation list named.

Python dict `==` ignores order, so even a non-crashing `same_items` would say `yes` while inner keys moved. Nested reorder is invisible **and** fatal.

### 2. `insertion-order` without `--obj` means "not sorted"

`classify` when `obj is None`:

```python
return "sorted-keys" if is_sorted else "insertion-order"
```

```bash
python3 "$CLI" '{2: 0, 0: 0, 1: 0}' '{1: 0, 0: 0, 2: 0}' '{0: 0, 1: 0, 2: 0}'
```

```text
display	0	{2: 0, 0: 0, 1: 0}	insertion-order
display	1	{1: 0, 0: 0, 2: 0}	insertion-order
display	2	{0: 0, 1: 0, 2: 0}	sorted-keys
same_items	yes
disagree	yes
# no reordered/faithful rows (two unsorted tuples; infer refuses)
rc=0
```

Two different permutations cannot both be the object's insertion order. A lone `{1: 0, 0: 0}` is also `insertion-order`, `reordered	none`, `faithful	0` — the only unsorted display is defined as insertion. That is unsupported certainty: the label reads as "this is how it was stored", not "keys are not sorted".

With `--obj '{2: 0, 0: 0, 1: 0}'` the middle permutation becomes `other`. The no-obj path has no `other`.

### 3. `disagree` is display-vs-display, not display-vs-object

```python
orders = [tuple(m) for _, m in parsed]
disagree = len(set(orders)) > 1
```

`--obj` is not in that set.

```bash
python3 "$CLI" --obj '{1: 0, 0: 0}' '{0: 0, 1: 0}'
```

```text
display	0	{0: 0, 1: 0}	sorted-keys
same_items	yes
disagree	no
reordered	0
faithful	none
rc=0
```

One sorted display of an insertion-ordered object: the printer reordered, `reordered` says so, `disagree` says no. Two copies of the sorted text still `disagree	no`. README documents "displayed key orders are not all the same"; next to `reordered` it is a lie about the object.

### 4. `reordered none` next to a real split: `other` is dropped

`reordered` is only `keys == sorted(obj)` and not insertion. Reverse-sorted / arbitrary permutation is `other`, then omitted from both summary rows.

```bash
python3 "$CLI" --obj '{1: 0, 0: 0, 2: 0}' '{2: 0, 1: 0, 0: 0}' '{1: 0, 0: 0, 2: 0}'
```

```text
display	0	{2: 0, 1: 0, 0: 0}	other
display	1	{1: 0, 0: 0, 2: 0}	insertion-order
disagree	yes
reordered	none
faithful	1
```

The printer that changed key order is unnamed. `reordered none` is unsupported certainty: it reads as "no display reordered", not "we only count `sorted()`".

Passing the **sorted** pytest line as `--obj` (the copying mistake the specimen exists to explain) hides the true insertion display the same way:

```bash
python3 "$CLI" --obj '{0: 0, 1: 0}' '{1: 0, 0: 0}' '{0: 0, 1: 0}'
```

```text
display	0	{1: 0, 0: 0}	other
display	1	{0: 0, 1: 0}	sorted-keys
reordered	none
faithful	1
```

CLI `--obj` also wins over a file `obj	` row, so a stale flag does this silently.

### 5. The origin's insertion evidence is a key list; the tool refuses it

specimen-034 OBSERVED:

```text
E       assert [0, 1] == [1, 0]
...
Falsifying example: test(
    d={0: 0, 1: 0},
)
d={1: 0, 0: 0}
```

`list(d)` is how insertion order showed up. The tool:

```bash
python3 "$CLI" --obj '{1: 0, 0: 0}' '[1, 0]' '{0: 0, 1: 0}'
# keyorder: not a mapping: '[1, 0]'
# rc=2
```

Sets, tuples, `OrderedDict(...)` : same. Feeding the pytest dump as `--file` dies on the first non-literal line (`@h.given(...)`), no skip. One bad line in an otherwise valid file (`pretty	{0: 0, 1: 0}` / `THIS IS BAD` / `repr	{1: 0, 0: 0}`) is rc=2, no partial report. Prefix strip is ASCII `NAME = {` only: `self.d = {…}`, `箱 = {…}`, `d: {…}`, `x = y = {…}` fail. Positional multiline `pprint` (`'{0: 0,\n 1: 0}'`) parses; the same text in `--file` is `not a mapping literal: '{1: 0,'`.

The three_views fixture works because a human already cut the three mapping lines out of the dump and named them. That extraction **is** the join the harvest promised. The CLI does not do it.

### 6. Misleading exit zero; empty `--file` lies

`disagree yes`, `same_items no`, `unsortable`, `other`, and `reordered none` next to a split are all rc=0. CANDIDATE's own suggested `--check` does not exist. Fine as a printer; hostile as a pipe predicate.

Empty existing file / comments-only / `obj` row with no displays / `--file /dev/null` / `--file -` with empty stdin:

```text
keyorder: need a mapping display, --file, or --fixture
rc=2
```

`--file` **was** given. Missing path is the honest `file not found` rc=1.

`--fixture --obj '{0: 0, 1: 0}'` ignores `--obj` (fixture overwrites after `args.obj`). `--fixture --file "$FX/agree.txt"` concatenates: `reordered	pretty	pretty	repr` — the already-sorted agree prints are counted as reorders against owned insertion `{1,0}`. Duplicate display name `pretty` can appear in **both** `reordered` and `faithful` (two rows, same label, opposite orders). File name `obj` is swallowed as `--obj`, not a printer (`reordered	none`, `faithful	none` on a same-items pair). UTF-8 BOM becomes printer `\ufeffpretty`. Leading tab on a named line splits to empty name + leftover `repr	{…}` parse error; empty name + mapping yields a `display` row with a shifted TSV and `reordered` with a blank field.

`{False: 1, 0: 2}` collapses on parse to `{False: 2}` and agrees with `{0: 2}` (`disagree	no`). `{True: 0, 0: 0}` vs obj `{1: 0, 0: 0}` is `insertion-order` / `faithful` because `True == 1`. `{1.0: 0, 0: 0}` same. Display text differs; identity does not.

Different items still get `sorted-keys` if their own keys sort: `--obj '{1: 0, 0: 0}' '{0: 1, 2: 3}'` → `display	sorted-keys`, `same_items	no`, no `reordered` row. Classification is not "this printer reordered **the object**".

5000-key file: rc=0, ~115k stdout, no cap. Not fatal; not a pipe component.

### 7. Unseen that is not a copy of `{1: 0, 0: 0}`

`pprint.pformat({3: 0, 1: 0, 2: 0})` is `{1: 0, 2: 0, 3: 0}` on this Python 3.14. `print`/`repr` keeps insertion. After pasting both literals, keyorder names display `0` as `sorted-keys` / `reordered`. That transfer is real and is **stdlib pprint**, not Hypothesis. It still requires the caller to already have both mapping texts on one line. `list({3:0,1:0,2:0})` is still rc=2.

specimen-012-style byte copies are not this lineage's problem; the owned fixture **is** the specimen-034 pair. Transfer to the dump blob, to `list(d)`, and to nested values was not run by the tests. 15 tests never hit unhashable values, `other`, disagree-vs-obj, dumps, or rc.

---

## Primitive

Reality-stripped operation: `ast.literal_eval` each supplied Python mapping literal; compare `tuple(keys)` to `tuple(sorted(keys))` and to `tuple(--obj)`; print TSV. Printer names are caller-supplied (`pretty	`, `--fixture` hardcodes them, positionals are `0`/`1`).

Nearest ordinary workflow:

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

`print(d)` vs `print(list(d))` vs `sorted(d)` is the same observation on one object. `pprint.pformat(d)` vs `repr(d)` is the same observation without Hypothesis. Observable capability lost if keyorder vanishes: the **named join** of several already-extracted mapping texts as `sorted-keys` / `insertion-order` / `reordered <name>`. That join is real on the owned pair and on transcribed three_views. It is not a dump parser, not a pretty-printer tracer, not a key-sequence classifier, not a nested-order walker.

That is why this is not KILL: the *question* (which displayed form of this mapping sorted keys, which preserved insertion, when they disagree) is a debugging object pytest and Hypothesis do not emit as a label. Copying the Falsifying example fails because the pretty printer sorted keys; naming that fact is the harvest. The current embodiment is a specimen-034 `literal_eval` replay that pretends "not sorted" is insertion provenance, that `disagree` looked at the object, and that `reordered none` means no printer moved keys.

The ceiling is already written down, and it is too small for the claim:

- "names the printer" + caller-supplied names → the tool labels key order of texts you already isolated; `--fixture` is the specimen hardcoded
- mapping literals only + line `--file` → origin dump, `list(d)`, multiline pprint, `self.d =` are rc=2
- `insertion-order` without obj → every unsorted permutation
- `reordered` = `sorted()` only → reverse / other / wrong `--obj` print `reordered none` beside `disagree yes`
- `disagree` skips `--obj` → one sorted display of an insertion object is `disagree no`
- `frozenset(items)` → nested values traceback; inner order invisible
- always rc=0 on a split → not a predicate
- research boundary (no pretty port, no pytest scrape) does not license refusing the key list the assertion already printed, or crashing on a nested dict

Do not merge this with a vendor pretty port, a Hypothesis checkout, or a pytest plugin. Do not merge onto `main`.

---

## Mutation (what must change)

Keep the object: for named displays of one mapping, say which texts are sorted-keys, which match insertion, which other permutation, and which names reordered.

Do not keep a `literal_eval` + `tuple == sorted` that only replays `{1: 0, 0: 0}` and prints `insertion-order` for "not sorted".

1. **Stop lying about insertion-order.** Without `--obj`, unsorted is `not-sorted` / `other`, never `insertion-order`. A lone mapping cannot be `faithful`. Two unsorted permutations cannot both be insertion. `reordered none` next to `disagree yes` is illegal: list `other` names, or print `reordered	<unseen>`.
2. **`disagree` includes the object.** One sorted display vs insertion `--obj` is `disagree	yes`. Wrong `--obj` (sorted line as original) must not hide the insertion text as `other` with `reordered none` unless the report says the obj keys are already sorted.
3. **Accept key sequences.** `[1, 0]`, `list(d)`, assertion lists are displays of key order. Specimen-034 `assert [0, 1] == [1, 0]` plus `d={1: 0, 0: 0}` plus the sorted falsifying mapping must join. Mapping-only remains a documented default; refusing the origin's insertion evidence is not a research boundary, it is a miss.
4. **Do not crash on nested.** `same_items` via order-insensitive equality that allows unhashable values. Nested mapping order is a row, or an explicit `outer-only` / `unseen-inner` refusal. Never a traceback. List values same.
5. **Dumps: skip or scan, don't die.** Non-mapping lines skipped (or `skipped	<line>`). Extract `NAME = {…}` / `NAME={…}` / a `{…}` blob from a pytest/Hypothesis dump without checking out Hypothesis. Multiline mapping in `--file` is one record, not a split on `{1: 0,`. ASCII-only prefix strip is not enough (`self.d`, unicode names). Still no pretty-printer port.
6. **Record, not a wall of text.** rc=1 when `disagree` is yes or a split is unnamed; rc=0 only when displays agree with obj (or with each other when no obj and none claim insertion). Cap `repr`. Quote TSV fields (empty name, BOM, tabs). Empty `--file` is `no mapping displays`, not "need --file". `--fixture` does not clobber `--obj` or silently concatenate. Name `obj` is a printer unless the row is a reserved first-column keyword documented as such. Duplicate names disambiguated. `--check` if you want a predicate; otherwise say the tool is not one.
7. **Identity of keys.** `True` vs `1`, `1.0` vs `1`, `False`+`0` collapse: either compare displayed key text, or emit `collapsed	True=1` instead of silent `faithful`. Duplicate keys in a literal (`{1: 0, 1: 9}`) are last-wins after parse; say so.
8. **Dogfood that is not `--fixture`.** Next unseen: `pprint.pformat` vs `repr` (stdlib already sorts on 3.14); `json.dumps(sort_keys=True)`; the specimen-034 dump **blob**; `list(d)` from the assertion; a nested dict value pair. Either name the reorder or refuse with a non-`none` row. Tests that never hit unhashable / `other` / dumps / rc are not a suite.

If the mutation cannot do (1)+(2)+(3), the object is still `list(d)==sorted(d)` with extra print, and a later destroyer should KILL. Do not merge.

---

MUTATE
