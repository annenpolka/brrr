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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
