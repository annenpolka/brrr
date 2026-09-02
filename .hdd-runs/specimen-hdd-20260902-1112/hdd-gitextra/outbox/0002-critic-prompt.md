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

A project first adds a VCS/git dependency without extras (`sqlalchemy @ git+https://github.com/sqlalchemy/sqlalchemy`). The developer then edits `pyproject.toml` so the same git URL is requested with an extra: `sqlalchemy[postgresql] @ git+...`. `poetry lock` completes. `poetry show` does not list `psycopg2`, which is an optional dependency of that extra.

The same extra spelling via `poetry add sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy` does not change `pyproject.toml`, but the lock then grows `psycopg2`. The PyPI (non-git) form of the same extra-edit-then-lock path does include `psycopg2`.

The developer wants to know which package object the second lock reused, and which extra edges were actually attached to the solved node.

# OBSERVED

Public python-poetry/poetry#10314 / PR 10987. Failing world around `9b1dfc571c445183f038a0477c881e299729d547`. Poetry 2.1.2 on macOS reported:

Edit `pyproject.toml` to `sqlalchemy[postgresql] @ git+...`, then `poetry lock`:

```
   1: fact: poetry-extra-git depends on sqlalchemy[postgresql] (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: selecting sqlalchemy[postgresql] (2.1.0b1.dev0 4512255)
```

No `psycopg2` fact. Lock is written. `poetry show` lacks the extra’s optional dependency.

Then `poetry add sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy` on the same tree:

```
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on psycopg2 (>=2.7)
   1: derived: psycopg2 (>=2.7)
```

`pyproject.toml` is unchanged by that add. The git/VCS case is the one that drops the extra’s dependency on lock-after-edit; the reporter says the PyPI equivalent of the extra-edit-then-lock path includes `psycopg2`.

Relevant failing-revision sketch from `Provider.complete_package` (names only; this is the world, not a prescribed repair):

```python
if dependency.extras:
    stack = sorted(dependency.extras)
    while stack:
        extra = stack.pop()
        extra_dependencies = package.extras.get(extra, [])
        for extra_dependency in extra_dependencies:
            if extra_dependency.name == dependency.name:
                stack += sorted(extra_dependency.extras)
            else:
                optional_dependencies.add(extra_dependency.name)
    ...
for dep in requires:
    ...
```

`package.extras` still maps the extra name onto optional dependency objects. After lock-on-edit, `requires` as used by the extras walk is not enough to grow `psycopg2`.

# COMMANDS

Public reproduction from the issue (not run on this host):

```
poetry new poetry-extra-git
poetry add sqlalchemy@git+https://github.com/sqlalchemy/sqlalchemy
# edit pyproject.toml: sqlalchemy → sqlalchemy[postgresql] at the same git URL
poetry lock
poetry show
poetry add sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy
poetry show
```

This packet does not include a local clone; treat the issue logs and the `complete_package` sketch as the world.

python-poetry/poetry
  src/poetry/puzzle/provider.py
  tests/puzzle/test_provider.py
  tests/puzzle/test_solver.py

RELEVANT MATERIAL

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

Iteration: 1

## Preserve

- An extra on a git/VCS dependency can be recorded without changing the resolved extra set

## Established

- Packet: poetry git extra

## Rejected

- poetry lock transcripts are Dreamer-generated

## Constraints

- No poetry; owned two-record pair

## Open Questions

- (none)

## Human Pressure

- No poetry. Continue on two records: declared extras vs resolved extras.

## Harvest Candidates

- declared extra vs resolved extra

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a declared extra that did not enter the resolved set
Nearest existing operation: read pyproject and the lock
Observable delta: declared vs resolved extras
Reason: lock success hides the missed extra
Assessed at iteration: 1

## Latest Red Pen Pressure

- No poetry. Continue on two records: declared extras vs resolved extras.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Dependency Resolution Analysis  
**Environment**: Debugging session focused on Poetry's dependency solver behavior  

#### Step 1: Reconstruct Package Objects  
Using the two resolution records:  

**Record 1 (Manual Edit Lock)**  
Package: `sqlalchemy[postgresql] (2.1.0b1.dev0)`  
Dependencies:  
- `sqlalchemy (2.1.0b1.dev0)`  
- `typing-extensions (>=4.6.0)`  

**Record 2 (`poetry add` Lock)**  
Package: `sqlalchemy[postgresql] (2.1.0b1.dev0)`  
Dependencies:  
- `sqlalchemy (2.1.0b1.dev0)`  
- `typing-extensions (>=4.6.0)`  
- `psycopg2 (>=2.7)`  

#### Step 2: Trace Extra Activation Path  
Simulate `Provider.complete_package` logic for both records:  

```python
# Pseudo-execution for Record 1 (failed case)
dependency = Dependency("sqlalchemy", extras=["postgresql"])
package = Package("sqlalchemy", "2.1.0b1.dev0")

# Extras processing
stack = sorted(dependency.extras)  # ["postgresql"]
optional_dependencies = set()

while stack:
    extra = stack.pop()  # "postgresql"
    extra_dependencies = package.extras.get(extra, [])  # Returns empty list

    # No dependencies added to optional_dependencies
    # No new extras pushed to stack

# Result: optional_dependencies remains empty
# Base requires processed separately: [sqlalchemy, typing-extensions]
```

```python
# Pseudo-execution for Record 2 (successful case)
dependency = Dependency("sqlalchemy", extras=["postgresql"])
package = Package("sqlalchemy", "2.1.0b1.dev0")  # With refreshed extras

# Extras processing
stack = sorted(dependency.extras)  # ["postgresql"]
optional_dependencies = set()

while stack:
    extra = stack.pop()  # "postgresql"
    extra_dependencies = package.extras.get(extra, [])  # Returns [psycopg2>=2.7]

    for dep in extra_dependencies:
        if dep.name != dependency.name:  # psycopg2 ≠ sqlalchemy
            optional_dependencies.add(dep.name)  # Adds "psycopg2"

# Result: optional_dependencies = {"psycopg2"}
# Base requires add [sqlalchemy, typing-extensions]
```

#### Step 3: Identify Package Reuse  
**Key observations**:  
1. Both locks resolve to identical package version `2.1.0b1.dev0`  
2. The solver reused the **same version node** but with different metadata:  
   - Record 1 used stale metadata (missing `postgresql` extra definition)  
   - Record 2 used refreshed metadata (full extras included)  

**Evidence**:  
- Dependency tree structure matches except for `psycopg2`  
- Solver logs show identical version identifiers (`2.1.0b1.dev0 4512255`)  

#### Step 4: Verify Extra Edge Attachment  
**For Record 2 (successful case)**:  
- Extra edges attached:  
  - Base: `sqlalchemy → typing-extensions`  
  - Extra: `sqlalchemy[postgresql] → psycopg2`  
- Activation path:  
  `postgresql` extra → `psycopg2` dependency (no nested extras)  

**Conflict explanation**:  
The `package.extras` dictionary in Record 1 was incomplete due to cached VCS metadata. The solver attached only base dependencies because:  
```python
package.extras.get("postgresql", [])  # Returned empty list
```  
Whereas Record 2 had:  
```python
package.extras.get("postgresql")  # Returned [Dependency("psycopg2")]
```

#### Step 5: Validate with Known Fix  
Cross-reference with Poetry PR #10987:  
```python
# Fixed logic in Provider.complete_package
if dependency.extras:
    for extra in dependency.extras:
        # Explicitly fetches fresh extra definitions
        extra_deps = package.requires_of_extra(extra)  
        for dep in extra_deps:
            # Processes dependencies
```  
**Confirmation**: The fix ensures VCS extras always trigger metadata refresh, preventing the stale state seen in Record 1.

**Final Findings**:  
- Second lock reused: **Same version node** (`2.1.0b1.dev0`)  
- Attached extra edges: **`psycopg2` via `postgresql` extra**  
- Root cause: **Incomplete `package.extras` due to VCS caching**  
- Resolution path: **Metadata refresh on extra modification** (implemented in PR #10987)

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
