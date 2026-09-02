# keyorder

origin.method: specimen-hdd
origin.trial: hdd-hypothesis
specimens: [specimen-034]

```yaml
origin:
  method: specimen-hdd
  trial: hdd-hypothesis
```

classification: USEFUL_COMPOSITION

## Primitive

Label each displayed mapping as sorted-keys vs insertion-order when those
views disagree.

## Why this might not exist

A pretty-printer can sort keys while the object that failed was insertion
ordered. `print(d)` and `print(list(d))` still leave which mapping display
reordered keys as a hand comparison.

## Core operation

Show which printed mapping is sorted and which preserves insertion order.

## Observable delta

One query names the printer that reordered keys.

## Reality mapping

Owned dict `{1: 0, 0: 0}` and two printers of that object. Displayed text is
a Python mapping literal; `ast.literal_eval` preserves displayed key order.

## Research boundary

Does not check out Hypothesis, run pytest, or port a vendor pretty-printer.

## Removed

Hypothesis checkout, pytest dump scraping, pretty-printer port.

## Smallest artifact

Python 3 stdlib CLI `keyorder`.

## Pre-implementation Reality assessment

See `REALITY.md`. Classification USEFUL_COMPOSITION. Nearest existing
operation: `print(d)` vs `print(list(d))`. Observable delta: one query
naming the printer that reordered keys. Constraint: no Hypothesis checkout;
an owned dict printer fixture is enough.

## How to run

From this directory:

```
python3 tests/test_keyorder.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `./demo.sh` twice (identical). Tests: 15 OK.

Before dogfood, prefixes failed:

```
python3 ./keyorder --obj '{1: 0, 0: 0}' 'd = {0: 0, 1: 0}' 'd={1: 0, 0: 0}'
keyorder: not a mapping literal: 'd = {0: 0, 1: 0}'
exit 2
```

After prefix stripping, `./demo.sh`:

```
== owned fixture .../keyorder/fixtures/two_prints.py ==
{0: 0, 1: 0}
{1: 0, 0: 0}

== nearest existing operation: print(d) vs print(list(d)) vs sorted(d) ==
print(d) {1: 0, 0: 0}
list(d) [1, 0]
sorted(d) [0, 1]

== keyorder --obj of those two prints ==
obj	{1: 0, 0: 0}
obj_keys	1	0
sorted_keys	0	1
display	pretty	{0: 0, 1: 0}	sorted-keys
display	repr	{1: 0, 0: 0}	insertion-order
same_items	yes
disagree	yes
reordered	pretty
faithful	repr

== keyorder --fixture (same owned dict, both printers) ==
obj	{1: 0, 0: 0}
obj_keys	1	0
sorted_keys	0	1
display	pretty	{0: 0, 1: 0}	sorted-keys
display	repr	{1: 0, 0: 0}	insertion-order
same_items	yes
disagree	yes
reordered	pretty
faithful	repr

== keyorder already-sorted {0: 0, 1: 0} (printers agree) ==
obj	{0: 0, 1: 0}
obj_keys	0	1
sorted_keys	0	1
display	pretty	{0: 0, 1: 0}	sorted-keys
display	repr	{0: 0, 1: 0}	sorted-keys
same_items	yes
disagree	no
reordered	none
faithful	pretty	repr

== keyorder prefixed views of the same owned dict ==
obj	{1: 0, 0: 0}
obj_keys	1	0
sorted_keys	0	1
display	pytest	{0: 0, 1: 0}	sorted-keys
display	note	{1: 0, 0: 0}	insertion-order
display	falsifying	{0: 0, 1: 0}	sorted-keys
same_items	yes
disagree	yes
reordered	pytest	falsifying
faithful	note
```

`print(d)` is `{1: 0, 0: 0}` and `list(d)` is `[1, 0]`. That does not label
the other mapping `{0: 0, 1: 0}` as sorted-keys. `keyorder` does, and names
`pretty` as `reordered`.

## Dogfood targets

Owned fixture `fixtures/two_prints.py`: `{1: 0, 0: 0}` printed with
`sorted(keys)` and with insertion order. First commit required a bare
`{…}` literal. After the prefix probe failed, `d = {…}` / `d={…}` /
trailing comma parse as the same owned prints.

## Surprises

`print(d)` is already the insertion mapping. The disagreeing mapping is
not `list(d)` — it is a second mapping printer that sorted keys.
Copying `{0: 0, 1: 0}` is a different dict under insertion-order
semantics than `{1: 0, 0: 0}`.

## Failures

Does not accept `list(d)` output as a mapping display. Does not parse a
full pytest dump, only a single `name = {…}` line.

## Suggested mutations

- `--check` exit 1 when `disagree` is yes
- Nested mapping value order
- Unsortable mixed-type keys as a first-class row

## Kill / keep

Keep: owned `{1: 0, 0: 0}` pair is `pretty` `sorted-keys` / `repr`
`insertion-order`, `reordered	pretty`. Prefixed pytest/falsifying views
of that same pair are both `reordered`; `note` is `faithful`.
