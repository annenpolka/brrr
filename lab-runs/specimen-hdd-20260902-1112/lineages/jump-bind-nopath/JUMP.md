# JUMP — bindname without stable path identity

HDD jump on a real survivor (`bindname` / candidate-bind).

Removed assumption:

```text
stable path identity does not exist
```

In-world facts used:

- modules can be loaded without a filesystem path
- leftover vs moved must still be asked when files have been concatenated
  into one module (no path split)

Not sent to R1 (R1 in flight / competing CLI first). Did not ask anyone to
“improve the tool.”

## Parent failure on the jump world

`bindname` keys identity on module path. `static_hits` last-wins per module.
On concatenated specimen-013 source it reports one `def parse` (the moved
body) and `same_function True`. The leftover helper is dropped. Stdin / a
loader with `origin=None` is not a query it can ask.

## Competing object

`bindslot`: slots of one name in one blob. Identity is slot index, not path.
Stdout has no `file` field. Source may be stdin, `--code`, or `--concat`.

## Isolation

Does not import the blob or any sibling. A concatenated `sys.exit` after the
leftover def does not hijack the query. `also` is leftover slots, collected
statically.

## Provenance

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  mutation: jump (stable path identity removed)
  parent: candidate-bind / bindname
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/jump-bind-nopath-nopath
branch: specimen-hdd/jump-bind-nopath-nopath
parent_commit: 432f954c0dce09f1b72084a66075051d884cba61
commit: see HEAD.txt
cli_sha256: 241c990ab5468ec37cfd84e46d5579971710d2125021075c70c6c91e4da57a5a
```

Not merged to `main`. Not installed on PATH. Not an R1 “improve the tool” turn.
