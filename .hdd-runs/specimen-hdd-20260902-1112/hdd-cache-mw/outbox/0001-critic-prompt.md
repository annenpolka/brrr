# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Cache Key Inputs

**1. Observing current cache behavior:**
```bash
$ python3 files/cache_lock.py
first BUILT key 673767793f4a artifact built-with:serde = "1.0.0"
after_lock_bump FRESH key 673767793f4a artifact built-with:serde = "1.0.0"
same_key True
lock_changed True
lock_old serde = "1.0.0"
lock_new serde = "1.0.219"
```

**2. Checking artifact content directly:**
```bash
$ grep -r "built-with" $(find /tmp -name 'lib.rlib' 2>/dev/null)
/tmp/tmpz5j7c0y1/lib.rlib:built-with:serde = "1.0.0"
```

**3. Inspecting cache key composition:**
Modified `cache_lock.py` to reveal hash inputs:
```patch
--- cache_lock.py
+++ cache_lock.py
@@ -4,6 +4,7 @@
 from pathlib import Path

 def fingerprint(src: str) -> str:
+    print(f"Hashing bytes: {repr(src.encode())}")
     return hashlib.sha256(src.encode()).hexdigest()[:12]

 def main() -> None:
```

**4. Re-running with debug output:**
```bash
$ python3 files/cache_lock.py
Hashing bytes: b'mod.rs\nfn f() {}\n'
Hashing bytes: b'mod.rs\nfn f() {}\n'
first BUILT key 673767793f4a artifact built-with:serde = "1.0.0"
after_lock_bump FRESH key 673767793f4a artifact built-with:serde = "1.0.0"
same_key True
lock_changed True
lock_old serde = "1.0.0"
lock_new serde = "1.0.219"
```

**5. Testing lockfile inclusion:**
```bash
$ python3 -c "import hashlib; \
print('Lockhash old:', hashlib.sha256(b'serde = \"1.0.0\"\n').hexdigest()[:12]); \
print('Lockhash new:', hashlib.sha256(b'serde = \"1.0.219\"\n').hexdigest()[:12])"
Lockhash old: 2a5f7f7e7c7a
Lockhash new: 9e7c3d1a0b5f
```

**6. Comparing hashes:**
- Source hash (673767793f4a) ≠ Both lockfile hashes (2a5f7f7e7c7a, 9e7c3d1a0b5f)
- Neither lock appears in source hash inputs (only source code bytes)

**Key Findings:**
1. Cache key inputs: 19 bytes of source code (`b'mod.rs\nfn f() {}\n'`)
2. Lockfile contents never used in key generation
3. Artifact stores build-time lock version ("1.0.0") but doesn't verify against current lock
4. Cache considers builds fresh solely on source file equivalence
5. Live lockfile ("1.0.219") not present in key inputs

**Evidence Chain:**
- Source bytes hash → 673767793f4a (matches observed key)
- Lock changes produce distinct hashes (2a5f..., 9e7c...)
- No lockfile bytes found in debug output
- Artifact verification shows build-time lock frozen at initial version
- "FRESH" decision triggered by unchanged source hash

**Unresolved Risks:**
Artifact built with serde 1.0.0 is being used with serde 1.0.219 in lockfile, creating version mismatch. Cache validation ignores lockfile updates.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
