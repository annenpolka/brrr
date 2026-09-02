# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A tiny crate cache reports freshness from a short hex identity. After the first build, only `Cargo.lock` (here, a one-line lockfile) changes: `serde = "1.0.0"` becomes `serde = "1.0.219"`. The second build prints FRESH. The artifact still says it was built with `1.0.0`.

The developer wants to know which bytes entered that identity, and whether the live lockfile is one of them.

# OBSERVED

Owned fixture files/cache_lock.py. Derived from specimen-006 (CI cache retaining superseded fingerprints across lockfile updates) by changing one axis: leftover *workspace member artifacts* vs a *lockfile-only* change against the same source tree.

## Captured host execution (stdlib, no third-party packages)
```
first BUILT key 673767793f4a artifact built-with:serde = "1.0.0"
after_lock_bump FRESH key 673767793f4a artifact built-with:serde = "1.0.0"
same_key True
lock_changed True
lock_old serde = "1.0.0"
lock_new serde = "1.0.219"
```

# COMMANDS

```
python3 files/cache_lock.py
```

files/cache_lock.py

RELEVANT MATERIAL

### cache_lock.py


#!/usr/bin/env python3
import hashlib
import tempfile
from pathlib import Path

def fingerprint(src: str) -> str:
    return hashlib.sha256(src.encode()).hexdigest()[:12]

def main() -> None:
    src = "mod.rs\nfn f() {}\n"
    lock_old = 'serde = "1.0.0"\n'
    lock_new = 'serde = "1.0.219"\n'
    with tempfile.TemporaryDirectory() as td:
        art = Path(td) / "lib.rlib"
        k1 = fingerprint(src)
        art.write_text("built-with:" + lock_old.strip())
        k2 = fingerprint(src)
        print("first BUILT key", k1, "artifact", art.read_text())
        print(
            "after_lock_bump",
            "FRESH" if k2 == k1 else "BUILT",
            "key",
            k2,
            "artifact",
            art.read_text(),
        )
        print("same_key", k1 == k2)
        print("lock_changed", lock_old != lock_new)
        print("lock_old", lock_old.strip())
        print("lock_new", lock_new.strip())

if __name__ == "__main__":
    main()

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
