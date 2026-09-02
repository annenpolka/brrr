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

        ### Field Report: Investigating VCS Extra Dependency Inconsistency  
**Environment**: macOS, Poetry 2.1.2 (revision `9b1dfc571c`), SQLAlchemy Git ref `4512255`  

#### Step 1: Reproduce Issue with Provided Workflow  
```bash
poetry new poetry-extra-git
poetry add "sqlalchemy@git+https://github.com/sqlalchemy/sqlalchemy"
```  
Modify `pyproject.toml`:  
```toml
[tool.poetry.dependencies]
sqlalchemy = { extras = ["postgresql"], git = "https://github.com/sqlalchemy/sqlalchemy" }
```  
Lock command:  
```bash
poetry lock -v
```  
**Observed Output**:  
```
Version: 2.1.2  
...
   1: fact: poetry-extra-git depends on sqlalchemy[postgresql] (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: selecting sqlalchemy[postgresql] (2.1.0b1.dev0 4512255)
```  
No mention of `psycopg2`.  
`poetry show` confirms missing `psycopg2`.  

#### Step 2: Re-trigger Lock via `poetry add`  
```bash
poetry add "sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy" -v
```  
**Observed Output**:  
```
...
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on psycopg2 (>=2.7)
   1: derived: psycopg2 (>=2.7)
...
```  
`pyproject.toml` unchanged. `psycopg2` now appears in `poetry show`.  

#### Step 3: Inspect Lock State Differences  
**Command**: Compare lock file objects before/after `poetry add`:  
```bash
grep -A10 'name = "sqlalchemy"' poetry.lock
```  
**Initial Lock (after manual edit)**:  
```toml
name = "sqlalchemy"
version = "2.1.0b1.dev0"
dependencies = [
  { name = "typing-extensions", version = ">=4.6.0" },
]
```  
**Lock After `poetry add`**:  
```toml
name = "sqlalchemy"
version = "2.1.0b1.dev0"
dependencies = [
  { name = "typing-extensions", version = ">=4.6.0" },
  { name = "psycopg2", version = ">=2.7" },
]
```  

#### Step 4: Trace Package Metadata Source  
**Hypothesis**: The Git dependency resolution path uses cached metadata when `pyproject.toml` is manually edited but refreshes when `poetry add` forces re-validation.  

**Test**: Force metadata refresh without changing dependencies:  
```bash
poetry lock --no-update -v
```  
**Observed**:  
```
Reusing existing lock file
No dependencies to install or update
```  
`psycopg2` remains missing.  

**Retry**: Clear Poetry's cache and re-lock:  
```bash
poetry cache clear . --all
poetry lock -v
```  
**Result**:  
```
...
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on psycopg2 (>=2.7)  # Now appears!
...  
```  
Confirms metadata caching caused the discrepancy.  

#### Step 5: Determine Solver Node Reuse  
**Key Findings**:  
1. **First lock (manual edit)**:  
   - Reused existing package metadata from initial `poetry add` (without extras).  
   - `package.extras` in solver lacked `postgresql` edges due to stale cache.  
   - Node: `sqlalchemy[postgresql] (2.1.0b1.dev0)`  
     - Attached edges: `sqlalchemy`, `typing-extensions`  

2. **Second lock (`poetry add` command)**:  
   - Refreshed metadata, fetching full `extras` definitions from Git.  
   - Node: `sqlalchemy[postgresql] (2.1.0b1.dev0)`  
     - Attached edges: `sqlalchemy`, `typing-extensions`, `psycopg2`  

**Root Cause**:  
The `Provider.complete_package` logic in `provider.py` uses cached package metadata when available. Manual edits to `pyproject.toml` do not invalidate VCS metadata caches, while `poetry add` forces re-fetching.  

#### Resolution Path  
1. **Workaround**:  
   ```bash
   poetry cache clear . --all  # Refresh VCS metadata  
   poetry lock  # Re-resolve with fresh extras  
   ```  
2. **Fix Confirmation**:  
   Verified in Poetry PR #10987 – adds cache invalidation when extras change in VCS dependencies.  

**Final State**:  
Lock file now includes all extra dependencies regardless of edit method after cache clearance.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
