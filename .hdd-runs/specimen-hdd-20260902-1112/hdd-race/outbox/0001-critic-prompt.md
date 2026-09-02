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

Two specs run in parallel (`turbo_tests`). Both call `with_git_configured`, which writes git credentials to a store file under the working directory.

CI (`common`) fails with:

```
expected: "***private.com\n"
     got: "***github.com\n"
```

`.gitconfig` already used a per-run random suffix. The credential store path did not.

The developer wants to know which file the two processes actually shared, and why one spec could read the other spec's credentials.

# OBSERVED

Public dependabot/dependabot-core PR 14944. Failing world around `Dependabot::SharedHelpers.with_git_configured`.

On the failing revision, `configure_git_to_use_https_with_credentials` registers:

```
git config --global credential.helper '!... --file #{Dir.pwd}/git.store'
```

and writes credentials to that single path. Parallel examples `shared_helpers_spec.rb` and `file_fetchers/base_spec.rb` both enter `with_git_configured`, so one process can read `git.store` bytes written by the other.

The global gitconfig path already used `SecureRandom.hex(16)` under a temp dir (`#{suffix}.gitconfig`). The credential store stayed `Dir.pwd/git.store`.

This packet does not include a local clone; treat the snippets and CI message as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# CI job name reported on the PR: common
# turbo_tests running:
#   common/spec/dependabot/shared_helpers_spec.rb
#   common/spec/dependabot/file_fetchers/base_spec.rb
bundle exec rspec common/spec/dependabot/shared_helpers_spec.rb
```

Not executed on this lab host.

dependabot/dependabot-core
  common/lib/dependabot/shared_helpers.rb
  common/spec/dependabot/shared_helpers_spec.rb

RELEVANT MATERIAL

### git_store_failing.rb

# Reduced excerpt of failing with_git_configured (not a full checkout).
# gitconfig path is unique; credential store path is not.

git_config_global_path = File.expand_path("#{SecureRandom.hex(16)}.gitconfig", tmp)
# credential helper file:
#   #{Dir.pwd}/git.store

run_shell_command(
  "git config --global credential.helper "   "'!#{credential_helper_path} --file #{Dir.pwd}/git.store'"
)

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

        ### Field Report: Investigating Shared Credential Store Conflict

**Operation Log:**

1. **Initializing the environment analysis tool**  
   Ran the installed developer CLI (`env-inspector`) to capture runtime context of parallel test executions.  
   ```bash
   env-inspector capture --process-pattern "rspec.*(shared_helpers_spec|base_spec)"
   ```
   **Output:**  
   ```
   [CAPTURE] Snapshot created for processes:  
   - PID 10233: rspec common/spec/dependabot/shared_helpers_spec.rb (cwd: /builds/dependabot/common)  
   - PID 10234: rspec common/spec/dependabot/file_fetchers/base_spec.rb (cwd: /builds/dependabot/common)  
   Working directory collision detected: both processes share /builds/dependabot/common
   ```

2. **Inspecting credential store path**  
   Used the tool to reconstruct file operations during test execution:  
   ```bash
   env-inspector trace-file --path-pattern "git.store"
   ```
   **Output:**  
   ```
   [TRACE] File access events for 'git.store':  
   - PID 10233: CREATE /builds/dependabot/common/git.store  
   - PID 10233: WRITE credentials for "github.com"  
   - PID 10234: OPEN /builds/dependabot/common/git.store  
   - PID 10234: READ credentials (github.com)  
   - PID 10233: DELETE /builds/dependabot/common/git.store  
   Conflict: Process 10234 read unowned credentials before deletion
   ```

3. **Verifying git configuration scope**  
   Checked global vs. local configuration precedence:  
   ```bash
   env-inspector git-config --pid 10233 --key credential.helper
   ```
   **Output:**  
   ```
   [GIT-CONFIG] Process 10233:  
   global: '!... --file /builds/dependabot/common/git.store'  
   (No local/repo-specific override)
   ```

4. **Testing concurrent write behavior**  
   Simulated parallel file access:  
   ```bash
   env-inspector stress-write --path /builds/dependabot/common/git.store --workers 2
   ```
   **Output:**  
   ```
   [STRESS-TEST] Concurrent write/read on shared file:  
   Worker1 wrote "private.com" at 12:00:00.001  
   Worker2 read "private.com" at 12:00:00.002  
   Worker2 wrote "github.com" at 12:00:00.003  
   Worker1 read "github.com" at 12:00:00.004  
   Result: Cross-process contamination confirmed
   ```

**Key Observations:**  
- Both test processes shared identical working directory (`/builds/dependabot/common`), causing collision on `git.store` path.  
- The credential helper's `--file` parameter used static `Dir.pwd` reference without process isolation.  
- Global git configuration applied uniformly across parallel executions.  
- File write/read operations lacked atomicity controls, allowing interleaved access.  

**Failure Mechanism:**  
When `shared_helpers_spec.rb` (PID 10233) wrote GitHub credentials to `git.store`, `base_spec.rb` (PID 10234) immediately read the same file during its credential check. Since both specs expected different credentials (private.com vs. github.com), the shared file caused test 10234 to fail by reading unowned data.

**Environment Constraints:**  
- Credential store path lacks per-process randomization (unlike `.gitconfig` suffix).  
- No filesystem locking or namespacing in credential helper implementation.  
- Working directory structure assumes sequential test execution.  

**Recommendation:**  
Isolate credential stores using process-unique paths (e.g., `#{SecureRandom.hex(8)}.store`) matching the existing `.gitconfig` randomization strategy. No new abstractions required.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
