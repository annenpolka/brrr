# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
