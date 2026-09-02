# adrid

origin.method: hdd
origin.trial: hdd-nixptr
specimens: [specimen-070]

classification: USEFUL_COMPOSITION

## Primitive

Given insert(addr, name) and later worker(addr, name), name when a pointer
address no longer names the same lock node, and which names were never fetched.

## Reality mapping

Owned events, not nix. Address equality is the wrong object.

## Removed

`nix flake prefetch-inputs --debug`, invented src patches.

## Smallest artifact

Python 3 stdlib CLI `addrid`.
