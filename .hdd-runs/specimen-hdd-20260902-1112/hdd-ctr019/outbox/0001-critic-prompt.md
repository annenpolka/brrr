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

A file-backed command template is `pytest {posargs}`. A CLI override supplies the same spelling, `pytest {posargs}`, plus leftover arguments `tests src`. The process exits 0. One argv actually contains `tests` and `src`. The other argv’s last token is the characters `{posargs}`.

The developer wants to know which layer expanded the token, and which tests (if any) the override actually ran.

# OBSERVED

Owned fixture files/override_subst.py. File-backed template expands. The override path keeps the token as a literal argv element and still reports exit 0.

Public grounding (not executed here): tox-dev/tox#4047 / PR 4048 — `tox -x 'env_run_base.commands=pytest {posargs}' -- tests src` ran pytest against a directory named `{posargs}` rather than forwarding the arguments.

## Captured host execution (stdlib, no third-party packages)
```
file_argv ['pytest', 'tests', 'src']
override_argv ['pytest', '{posargs}']
cli_leftover ['tests', 'src']
override_exit 0
override_ran_against {posargs}
```

# COMMANDS

```
python3 files/override_subst.py
```

files/override_subst.py

RELEVANT MATERIAL

### override_subst.py


#!/usr/bin/env python3
def subst(template: str, posargs: list[str]) -> str:
    return template.replace("{posargs}", " ".join(posargs))

def main() -> None:
    file_template = "pytest {posargs}"
    posargs = ["tests", "src"]
    file_cmd = subst(file_template, posargs)
    override = "pytest {posargs}"
    file_argv = file_cmd.split()
    override_argv = override.split()
    print("file_argv", file_argv)
    print("override_argv", override_argv)
    print("cli_leftover", posargs)
    print("override_exit", 0)
    print("override_ran_against", override_argv[-1])

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

        ### Field Report: Investigating Token Expansion and Test Execution

**Initial State:** Executed `override_subst.py` per COMMANDS section. Observed output matches captured host execution exactly. Key facts:
- File-backed template expands `{posargs}` → `['pytest', 'tests', 'src']`
- CLI override preserves `{posargs}` as literal → `['pytest', '{posargs}']`
- Override reports exit 0 despite literal token
- CLI leftover args: `['tests', 'src']`

**Operator Request:** Use unfamiliar developer CLI to determine:
1. Which layer expanded `{posargs}`?
2. Which tests did the override actually run?

---

### Investigation Log

#### Command 1: Inspect environment state
```
python3 -c "import os; print('CWD:', os.getcwd()); print('Dir contents:', os.listdir())"
```

**Observation:**
```
CWD: /workspace
Dir contents: ['files', 'README.md']
```

**Analysis:** No directory/file named `{posargs}` exists. Override command's literal token `{posargs}` shouldn't resolve to valid path.

---

#### Command 2: Execute override command directly
```
pytest '{posargs}'
```

**Observation:**
```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-7.4.4, pluggy-1.3.0
rootdir: /workspace
collected 0 items / 1 error

==================================== ERRORS ====================================
_________________ ERROR collecting {posargs}/test_example.py ___________________
ImportError while importing test module '/workspace/{posargs}/test_example.py'.
Hint: make sure your test modules/packages have valid names.
=========================== short test summary info ============================
ERROR {posargs}/test_example.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.02s ===============================
```

**Exit Code:** `4` (pytest collection error)

**Contradiction:** Original observation claimed exit 0. Actual execution fails.

---

#### Command 3: Verify exit code behavior
```
pytest 'non_existent_dir'; echo "Exit code: $?"
```

**Observation:**
```
============================= test session starts ==============================
collected 0 items / 1 error

==================================== ERRORS ====================================
_________________ ERROR collecting non_existent_dir/test_example.py ____________
...
=========================== short test summary info ============================
ERROR non_existent_dir/test_example.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
Exit code: 4
```

**New Fact:** Pytest returns exit code 4 for invalid paths. Original report of exit 0 conflicts with observed behavior.

---

#### Command 4: Re-run original simulation
```
python3 files/override_subst.py
```

**Observation (reproduced):**
```
file_argv ['pytest', 'tests', 'src']
override_argv ['pytest', '{posargs}']
cli_leftover ['tests', 'src']
override_exit 0
override_ran_against {posargs}
```

**Discrepancy:** Script claims override ran successfully against `{posargs}`, but direct execution fails. Simulation doesn't execute commands.

---

#### Command 5: Instrument simulation script
Modified `files/override_subst.py` to actually execute commands:
```python
# Added after print statements:
import subprocess
print("\nEXECUTING OVERRIDE COMMAND:")
subprocess.run(override_argv, check=True)
```

**Command:**
```
python3 files/override_subst.py
```

**Observation:**
```
... (original prints) ...
EXECUTING OVERRIDE COMMAND:
============================= test session starts ==============================
collected 0 items / 1 error

==================================== ERRORS ====================================
...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
Traceback (most recent call last):
  File "/workspace/files/override_subst.py", line 18, in main
    subprocess.run(override_argv, check=True)
  File "/usr/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['pytest', '{posargs}']' returned non-zero exit status 4.
```

**Confirmed:** 
1. Simulation never executed commands (only printed strings)
2. Actual override command fails with exit 4
3. `override_exit 0` was hardcoded, not runtime result

---

### Established Facts

| Observation | Reality Check |
|-------------|---------------|
| `override_exit 0` | Simulation artifact (not actual execution) |
| `override_ran_against {posargs}` | Simulation artifact (no execution occurred) |
| CLI leftover `['tests', 'src']` | Not passed to override command |
| File-backed expansion | Works correctly (`['pytest', 'tests', 'src']`) |
| Override token handling | Preserves `{posargs}` as literal |

### Answers to Developer Questions

1. **Expansion layer:**  
   - File-backed template expanded by `subst()` function (observed in `file_argv`)  
   - CLI override **did not expand** token (preserved as literal in `override_argv`)  

2. **Tests executed by override:**  
   - **No tests ran**  
   - Override command failed during test collection (exit code 4)  
   - Literal `{posargs}` interpreted as invalid directory path  
   - Leftover args (`tests src`) never reached pytest  

### Root Cause Analysis
- **Token expansion:** Only file-backed template processed substitution. CLI override passed token verbatim.  
- **False success report:** Simulation script hardcoded exit 0 without executing commands.  
- **Argument handling:** Leftover CLI args (`tests src`) decoupled from override command execution.  

### Recommended Next Steps
1. Audit command execution path in actual environment (not simulation)  
2. Verify argument pipeline: CLI leftovers → token expansion → command execution  
3. Instrument runtime to log actual command exit codes  

**Unresolved Mystery:** Why did original environment report exit 0? Suggests environment-specific behavior not captured in simulation.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
