CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A unified-diff hunk `@@ -2,0 +3 @@` plus `+inserted` is applied to `first\nsecond\nthird\n`. The applier reports success (exit 0), including a frozen-lockfile-style install path. The resulting bytes are not the file the hunk coordinates name.

The developer wants to know which original line the empty old-range was treated as, and why success did not mean the recorded gap.

# OBSERVED

Owned fixture files/patch_insert.py. Transfer of pnpm/pnpm#14343 (Rust patch applier in a Node package-manager install) into a stdlib Python applier.

Public contrast from that PR (not a local pnpm run): given `first\nsecond\nthird\n`, hunk `@@ -2,0 +3 @@` / `+inserted` must yield `first\nsecond\ninserted\nthird\n`. The affected applier yielded `first\ninserted\nsecond\nthird\n` and still reported a successful install, including `--frozen-lockfile`.

## Captured host execution (stdlib, no third-party packages)
```
orig 'first\nsecond\nthird\n'
hunk @@ -2,0 +3 @@ +inserted
result 'first\ninserted\nsecond\nthird\n'
apply_exit 0
frozen_lockfile_install success
```

# COMMANDS

```
python3 files/patch_insert.py
```

files/patch_insert.py

RELEVANT MATERIAL

### patch_insert.py


#!/usr/bin/env python3
def apply_hunk(text: str, old_start: int, old_count: int, insert: str) -> str:
    lines = text.splitlines(keepends=True)
    idx = old_start - 1
    if not insert.endswith("\n"):
        insert += "\n"
    lines.insert(idx, insert)
    return "".join(lines)

def main() -> None:
    orig = "first\nsecond\nthird\n"
    out = apply_hunk(orig, old_start=2, old_count=0, insert="inserted\n")
    print("orig", repr(orig))
    print("hunk", "@@ -2,0 +3 @@ +inserted")
    print("result", repr(out))
    print("apply_exit", 0)
    print("frozen_lockfile_install", "success")

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
