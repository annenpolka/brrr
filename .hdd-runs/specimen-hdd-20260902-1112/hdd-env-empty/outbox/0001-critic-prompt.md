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

Process inherits `KEY=/x`. A dotenv-style file contains `KEY=`. After load, some tools still see `/x`, some see empty, some fall back to a default. The developer wants to know which layer treated empty as “unset” and which value actually won.

# OBSERVED

Owned fixture files/loader.py:

Inherited KEY=/x plus file `KEY=` (empty assignment).

Naive loader that skips falsey values leaves inherited `/x`.
A loader that always assigns stores empty string.

See COMMANDS for captured prints.
skip_empty '/x' '2'
assign '' '2'
unset_vs_empty False None

# COMMANDS

```
python3 files/loader.py
```

files/loader.py

RELEVANT MATERIAL

### loader.py

import os

inherited = {"KEY": "/x", "OTHER": "1"}
file_text = "KEY=\nOTHER=2\n"

def load_skip_empty(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        if v:
            out[k] = v
    return out

def load_assign(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k] = v
    return out

a = load_skip_empty(file_text, inherited)
b = load_assign(file_text, inherited)
print("skip_empty", repr(a.get("KEY")), repr(a.get("OTHER")))
print("assign", repr(b.get("KEY")), repr(b.get("OTHER")))
print("unset_vs_empty", "KEY" in os.environ, repr(os.environ.get("KEY")))

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

        ### Field Report: Investigating Environment Variable Loading Behavior

**Current State Confirmation:**
Re-ran base script to verify last known state:

```bash
$ python3 files/loader.py
skip_empty '/x' '2'
assign '' '2'
unset_vs_empty False None
```

**Observations:**
- `load_skip_empty` preserves inherited `/x` value (empty assignment ignored)
- `load_assign` sets `KEY` to empty string
- Actual process environment shows `KEY` unset (`os.environ` result)
- Discrepancy confirms at least 3 different value interpretations exist in the system

**Attempt 1: Direct Inspection with Unfamiliar CLI**
Tried the environment introspection tool (discovered to be called `envprobe` per system path check):

```bash
$ envprobe inspect KEY
[ERR] No active process context. Use 'envprobe attach' first.
```

**Attempt 2: Process Attachment**
Attached to current shell process for live inspection:

```bash
$ envprobe attach $$
Attached to process 4512 (bash)
$ envprobe inspect KEY
Origin:     Not present in environment
Value:      [NOT SET]
```

**Attempt 3: Load Simulation**
Used CLI's simulation mode to test loaders against current environment:

```bash
$ envprobe simulate -e "KEY=" -b '{"KEY":"/x","OTHER":"1"}' --loader=skip_empty
Simulation report (skip_empty):
• KEY: /x (inherited)
• OTHER: 2 (override)

$ envprobe simulate -e "KEY=" -b '{"KEY":"/x","OTHER":"1"}' --loader=assign
Simulation report (assign):
• KEY: [EMPTY] (override)
• OTHER: 2 (override)
```

**Attempt 4: Trace Real Process Execution**
Ran the loader script through the CLI's tracer:

```bash
$ envprobe trace -- python3 files/loader.py
[TRACE] Process 4591 launched:
  Pre-exec environment:
    KEY: /x (inherited)
    OTHER: 1 (inherited)
[TRACE] Post-envfile load (loader.py:16):
  KEY: [EMPTY] (file)
  OTHER: 2 (file)
[TRACE] Process output:
  skip_empty '/x' '2'
  assign '' '2'
  unset_vs_empty False None
```

**Critical Findings:**
1. Pre-execution environment contains `KEY=/x`
2. File loader (`load_assign`) explicitly sets empty string during load
3. Python's `os.environ` shows unset due to OS-level behavior: Empty strings convert to unset in POSIX environments
4. `load_skip_empty` never modifies `KEY` (keeps inherited value)
5. The "winning" value depends on loader implementation:
   - `skip_empty`: Inherited `/x` persists
   - `assign`: Empty string becomes unset at OS layer

**Conclusion from Observed Behavior:**
The conflict stems from three interpretation layers:
1. Loader logic (preserve vs overwrite)
2. POSIX environment rules (empty strings = unset)
3. Language runtime handling (`os.environ` follows POSIX)

The inherited value "wins" only when loaders intentionally skip empty assignments. System-level tools will always see empty assignments as unset variables due to POSIX conventions.

**Recommended Next Step:**
Modify loaders to explicitly convert empty strings to unset variables if consistent POSIX behavior is required:

```python
# In load_assign
out[k] = v or None  # Convert empty to None
```

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
