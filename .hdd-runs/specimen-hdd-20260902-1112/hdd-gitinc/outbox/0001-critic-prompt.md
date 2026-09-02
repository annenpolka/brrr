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

`actions/checkout` v7 on a self-hosted Windows runner writes `includeIf.gitdir:...path` entries pointing at a temp credentials config:

```
includeIf.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
```

Post-job cleanup runs the equivalent of:

```
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
```

Git prints:

```
error: invalid pattern: C:\runner\_work\_temp\git-credentials-.config
```

The workflow can still conclude successfully. A later checkout on the same worktree sees the leftover `includeIf` and repeats the error.

The developer wants to know which git config *value* cleanup tried to match, whether that value was treated as a regex, and which `includeIf` entries remained.

# OBSERVED

Public actions/checkout#2528 / PR 2530. Failing world in `src/git-command-manager.ts` `tryConfigUnsetValue`.

On the failing revision:

```
args.push('--unset', configKey, configValue)
const output = await this.execGit(args, true)
return output.exitCode === 0
```

Git's `git config --unset <name> <value-pattern>` treats the third argument as a regular expression. Native Windows paths contain `\`. `\` is an invalid regex escape here, so git reports `error: invalid pattern` and does not remove the entry.

`tryConfigUnsetValue` passes `true` as the allow-failure flag to `execGit`, so a nonzero git exit becomes a boolean false rather than a thrown failure. Cleanup continues.

Sibling helper `tryConfigUnset` uses `--unset-all` with only the key (no value pattern).

v5.0.1 on the same runner does not take this v7 credential-layout cleanup path; no invalid-pattern message and no leftover includeIf.

This packet does not include a local clone; treat the snippets and git error as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
# error: invalid pattern: C:\runner\_work\_temp\git-credentials-.config
git config --local --get-regexp includeif
```

Not executed on this lab host.

actions/checkout
  src/git-command-manager.ts
  dist/index.js

RELEVANT MATERIAL

### cleanup_error.txt

git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
error: invalid pattern: C:\runner\_work\_temp\git-credentials-.config

### tryConfigUnsetValue_failing.ts

// Reduced excerpt on failing_ref
// src/git-command-manager.ts

async tryConfigUnsetValue(
  configKey: string,
  configValue: string,
  globalConfig?: boolean,
  configFile?: string
): Promise<boolean> {
  const args = ['config']
  if (configFile) {
    args.push('--file', configFile)
  } else {
    args.push(globalConfig ? '--global' : '--local')
  }
  args.push('--unset', configKey, configValue)
  const output = await this.execGit(args, true)
  return output.exitCode === 0
}

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

        ### Field Report: Git Configuration Cleanup Investigation  
**Operating Environment**: Self-hosted Windows runner with `actions/checkout@v7`. Post-job cleanup failed due to invalid regex pattern in Git config unset command.  

---

#### **Step 1: Inspect Residual `includeIf` Entries**  
**Command**:  
```bash
git config --local --get-regexp includeif
```  
**Output**:  
```plaintext
includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
```  
**Observation**:  
The `includeIf` entry persists exactly as described in the cleanup error. The key uses forward slashes (`C:/...`), while the value uses backslashes (`C:\...`).  

---

#### **Step 2: Verify Git's Value-Matching Behavior**  
**Command**:  
```bash
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path "C:\\runner\\_work\\_temp\\git-credentials-.config"
```  
**Output**:  
```plaintext
error: invalid pattern: C:\\runner\\_work\\_temp\\git-credentials-.config
```  
**Observation**:  
- Git treats the value argument (`C:\...`) as a **regex pattern**, not a literal string.  
- Backslashes (`\`) are regex escape characters. The sequence `\_` is invalid (no escaped `_` exists), causing the error.  
- Double-backslash escape attempts (e.g., `\\`) still fail—Git expects valid regex syntax.  

---

#### **Step 3: Retry Unset Without Value Pattern**  
**Command**:  
```bash
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path
```  
**Output**: *(no output, exit code `0`)*  

**Verification**:  
```bash
git config --local --get-regexp includeif
```  
**Output**: *(no results)*  

**Observation**:  
- Using `--unset` **without** the value pattern succeeds. The key alone is sufficient for removal.  
- The leftover `includeIf` entry is now cleared.  

---

#### **Step 4: Confirm Value Matching Logic**  
**Command**: *(Simulate original failure in a test repo)*  
```bash
git config --local includeIf.gitdir:C:/test/.git.path "C:\temp\file.config"
git config --local --unset includeIf.gitdir:C:/test/.git.path "C:\temp\file.config"
```  
**Output**:  
```plaintext
error: invalid pattern: C:\temp\file.config
```  
**Observation**:  
- Git explicitly logs the **value pattern** it tried to match: `C:\temp\file.config`.  
- The value is treated as regex, and backslashes break parsing.  

---

### **Summary of Findings**  
| **Question**                                       | **Answer**                                                                 |
|----------------------------------------------------|----------------------------------------------------------------------------|
| **Config value cleanup tried to match**            | `C:\runner\_work\_temp\git-credentials-.config` (literal path string).    |
| **Was the value treated as regex?**                | **Yes**—Git `--unset <key> <value>` interprets `<value>` as regex.         |
| **Residual `includeIf` entries post-cleanup**      | One entry: `includeif.gitdir:C:/runner/_work/repo/repo/.git.path` → `C:\runner\_work\_temp\git-credentials-.config`. |

**Root Cause**:  
Cleanup used `git config --unset <key> <value>` where `<value>` contained Windows backslashes (`\`), which Git misinterprets as invalid regex escapes. The `actions/checkout` code suppresses this error (`allow-failure: true`), leaving the entry intact.  

**Recommendation**:  
Use `--unset-all <key>` (no value pattern) for paths. This matches the safe `tryConfigUnset` method observed in `actions/checkout`’s code.  

**Environment State**:  
Residual `includeIf` entry manually cleared. No further errors detected.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
