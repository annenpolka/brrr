# bindslot

origin.method: specimen-hdd
origin.trial: hdd-identity
origin.mutation: jump (stable path identity removed)
parent: candidate-bind / bindname
specimens: [specimen-013 concatenated; pathless load]

classification: USEFUL_COMPOSITION

## Core operation

For a name in one module, show every binding slot and the body that would
run. Distinguish leftover same-name helpers from the moved definition when
there is no path split.

## Observable delta

Concatenating `pkg_util.py` and `pkg_parse.py` (or exec of that blob with no
`__file__`) leaves two `def parse` in one module. `grep def parse` hits both.
Last-wins import binds the moved body. bindslot prints both slots, marks the
last as `runs` and the earlier as `leftover`, and `same_function False`.

A path-keyed scan last-wins per module and reports one identity.

## Reality mapping

AST-scan one source blob for module-namespace bindings of the name, including
compound wrappers (`If`/`Try`/...). Last slot is what would run if the module
finished. Earlier same-name defs are leftovers. No import, no `sys.path`, no
file identity.

## Research boundary

Does not reconstruct git moves. Does not execute the blob (so a `raise`
before the last def is not observed; slots are source order). Nested defs
inside another function or class are not module bindings. Does not recover
source from a live module that has already forgotten it.

## Removed

stable path identity; tree-wide import of every same-name hit.

## Smallest artifact

Python 3 stdlib CLI `bindslot`.

## How to run

From this directory:

```
python3 tests/test_bindslot.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `./demo.sh` ×2, logs byte-identical.

Concatenated specimen-013 plus `exec` with no `__file__`: `parse('  z  ')` is `('moved', 'z')`.

`bindslot parse --concat pkg_util.py --concat pkg_parse.py`:

```
name	parse
slots	2
runs_slot	1
same_function	False
role	leftover	source legacy
role	runs	source moved
```

Pathless stdin of the same blob: two slots, leftover vs runs, no `file` field.

Parent `bindname -C concat_dir parse`: `count 1`, `same_function True`, only the moved body, `file concat.py`.

Tests: 17 OK.

## Kill / keep

Keep as a competing jump: leftover vs moved survives when path identity is gone.
A path-keyed last-wins scan is not this object.
