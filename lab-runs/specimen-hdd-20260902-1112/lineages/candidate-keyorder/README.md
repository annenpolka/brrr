# keyorder

Label each displayed mapping as **sorted-keys** or **insertion-order** when
those views disagree, and name the printer that reordered keys.

`print(d)` shows insertion order. `print(list(d))` shows the keys, not a
second mapping. A pretty-printer that sorts keys makes a different mapping
text from the object that failed. This query is the join.

Owned fixture: `{1: 0, 0: 0}` printed once with `sorted(keys)` and once in
insertion order.

## Usage

```
keyorder [--obj MAPPING] MAPPING [MAPPING ...]
keyorder [--obj MAPPING] --file PATH
keyorder --fixture
```

| argument | meaning |
| --- | --- |
| `MAPPING` | displayed Python mapping literal; key order in the text is the displayed order. `d = {…}` and `d={…}` prefixes (and a trailing comma) are stripped |
| `--obj MAPPING` | original mapping (insertion order). If omitted, inferred from the unique unsorted display |
| `--file PATH` | lines of `MAPPING` or `NAME<TAB>MAPPING`. `obj<TAB>MAPPING` sets `--obj`. `#` comments skipped |
| `--fixture` | owned `{1: 0, 0: 0}`: printer `pretty` sorts keys, printer `repr` preserves insertion |

## Output

Tab-separated rows.

```
obj	{1: 0, 0: 0}
obj_keys	1	0
sorted_keys	0	1
display	pretty	{0: 0, 1: 0}	sorted-keys
display	repr	{1: 0, 0: 0}	insertion-order
same_items	yes
disagree	yes
reordered	pretty
faithful	repr
```

| row | meaning |
| --- | --- |
| `display` | name, formatted mapping, `sorted-keys` / `insertion-order` / `other` / `unsortable` |
| `disagree` | `yes` when displayed key orders are not all the same |
| `reordered` | displays whose keys are sorted and not the original insertion order |
| `faithful` | displays whose keys match original insertion order |

## Examples

Owned fixture — two prints of `{1: 0, 0: 0}`:

```
keyorder --obj '{1: 0, 0: 0}' --file fixtures/two_prints.txt
# display	pretty	{0: 0, 1: 0}	sorted-keys
# display	repr	{1: 0, 0: 0}	insertion-order
# reordered	pretty
```

Same owned printers, no file:

```
keyorder --fixture
```

Already-sorted `{0: 0, 1: 0}`: both printers emit the same text.

```
keyorder --obj '{0: 0, 1: 0}' --file fixtures/agree.txt
# disagree	no
# reordered	none
```

Prefixed views of the same owned dict (`d = {…}` / `d={…}`):

```
keyorder --file fixtures/three_views.txt
# reordered	pytest	falsifying
# faithful	note
```

## Boundary

Does not run Hypothesis or pytest. Does not port a vendor pretty-printer.
The owned printers are the world. Mapping literals only (not JSON, not
`list(d)`).
