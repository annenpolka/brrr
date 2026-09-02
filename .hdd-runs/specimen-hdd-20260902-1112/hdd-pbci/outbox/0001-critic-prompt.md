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

Protobuf keeps checked-in generated files in sync via Bazel targets tagged `staleness_test` and a helper `./regenerate_stale_files.sh`. GitHub Actions workflow `.github/workflows/staleness_check.yml` is supposed to fail scheduled/manual runs when those targets fail.

Operators still see the job conclusion as success on a revision where generated outputs do not match the generators. The step log can include the sentence `Please run ./regenerate_stale_files.sh to regenerate stale files`.

The developer wants to know what exit status the workflow step actually used, and how that relates to the Bazel test exit status.

# OBSERVED

Public PR protocolbuffers/protobuf#15983. Failing workflow file is on `99c55ba3256c0bfbfa7678150171a11e9a47af58`.

Job `Test staleness` / step `Run all staleness tests` uses `protocolbuffers/protobuf-ci/bazel@v2` with bash:

```
set -ex;
if [[ -z $COMMIT_TRIGGERED_RUN || -z $MAIN_RUN ]]; then
bazel query 'attr(tags, "staleness_test", //...)' | xargs bazel test $BAZEL_FLAGS ||
echo "Please run ./regenerate_stale_files.sh to regenerate stale files";
else
bazel query 'attr(tags, "staleness_test", //...)';
fi
```

`COMMIT_TRIGGERED_RUN` is set only when the event is not `schedule` / `workflow_dispatch`. `MAIN_RUN` is set when the ref is `main`. Scheduled nightly therefore takes the first branch (the query + `bazel test` line).

The workflow file comment says scheduled/manual runs should make sure there are no stale files. The observed Actions conclusion on a stale tree can still be success while the echo line is present in the log.

# COMMANDS

```
git checkout 99c55ba3256c0bfbfa7678150171a11e9a47af58
# inspect:
.github/workflows/staleness_check.yml
# intended local analogue of the scheduled branch (full repo build; not run here):
bazel query 'attr(tags, "staleness_test", //...)' | xargs bazel test
echo pipeline_status:$?
```

This packet does not execute Bazel or GitHub Actions. Treat the workflow file and the green-job-plus-echo observation as the world.

protocolbuffers/protobuf @ 99c55ba3256c0bfbfa7678150171a11e9a47af58
  .github/workflows/staleness_check.yml
  regenerate_stale_files.sh

RELEVANT MATERIAL

### workflows/staleness_check.yml

# original path in repo: .github/workflows/staleness_check.yml @ 99c55ba3256c0bfbfa7678150171a11e9a47af58
name: Staleness tests

on:
  schedule:
    # Run daily at 10 AM UTC (2 AM PDT)
    - cron: 0 10 * * *
  workflow_call:
    inputs:
      safe-checkout:
        required: false
        description: "The SHA key for the commit we want to run over"
        type: string
  workflow_dispatch:

permissions: {}
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        branch: [main, 22.x, 23.x, 24.x, 25.x]
        os: [{ name: Linux, value: ubuntu-latest}]

    name: Test staleness ${{ matrix.os.name }} ${{ github.head_ref && 'PR' || matrix.branch }}
    runs-on: ${{ matrix.os.value }}
    if: ${{ github.event.repository.full_name == 'protocolbuffers/protobuf' }}
    steps:
      - name: Checkout ${{ github.head_ref && 'PR' || matrix.branch }}
        uses: protocolbuffers/protobuf-ci/checkout@v2
        with:
          ref: ${{ inputs.safe-checkout || github.head_ref || matrix.branch }}

      - name: Mark runs associated with commits
        if: ${{ github.event_name != 'schedule' && github.event_name != 'workflow_dispatch' }}
        run: echo "COMMIT_TRIGGERED_RUN=1" >> $GITHUB_ENV

      - name: Mark runs from the main branch
        if: ${{ github.base_ref == 'main' || github.ref == 'refs/heads/main' }}
        run: echo "MAIN_RUN=1" >> $GITHUB_ENV

      - name: Run all staleness tests
        # Run all tests if either of the following is true, otherwise simply run the query to make
        # sure it continues to work:
        # 1) If this is not a commit-based run it means it's scheduled or manually dispatched. In
        #    this case we want to make sure there are no stale files.
        # 2) Release branches don't work with automated commits (see b/287117570).  Until this is
        #    fixed, we want to run the tests to force manual regeneration when necessary.
        #
        # In branches where automatic updates work as post-submits, we don't want to run staleness
        # tests along with user changes.  Any stale files will be automatically fixed in a follow-up
        # commit.
        uses: protocolbuffers/protobuf-ci/bazel@v2
        with:
          credentials: ${{ secrets.GAR_SERVICE_ACCOUNT }}
          bazel-cache: staleness
          bash: >
            set -ex;
            if [[ -z $COMMIT_TRIGGERED_RUN || -z $MAIN_RUN ]]; then
            bazel query 'attr(tags, "staleness_test", //...)' | xargs bazel test $BAZEL_FLAGS ||
            echo "Please run ./regenerate_stale_files.sh to regenerate stale files";
            else
            bazel query 'attr(tags, "staleness_test", //...)';
            fi

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

        ### Field Report: Investigating Workflow Step Exit Status

**Command Sequence Executed:**
```bash
# Inspect workflow step exit behavior simulation
cat << 'EOF' > test_step.sh
set -ex
if true; then  # Simulating scheduled run condition
  # Simulate Bazel test failure (non-zero exit)
  echo "Simulating: bazel test returns 1 (stale files detected)"
  exit 1
else
  true
fi || echo "Please run ./regenerate_stale_files.sh to regenerate stale files"
EOF

# Execute simulated workflow step
chmod +x test_step.sh
./test_step.sh
echo "Observed step exit status: $?"
```

**Output Observed:**
```
+ true
+ echo 'Simulating: bazel test returns 1 (stale files detected)'
Simulating: bazel test returns 1 (stale files detected)
+ exit 1
+ echo 'Please run ./regenerate_stale_files.sh to regenerate stale files'
Please run ./regenerate_stale_files.sh to regenerate stale files
Observed step exit status: 0
```

**Failure Analysis:**
1. The `||` operator in the workflow script creates a *conditional success pathway*:
   - When Bazel tests fail (exit ≠0), the `echo` command executes
   - The `echo` command always exits with status 0
   - The entire compound command inherits the last command's exit status

2. Workflow step behavior:
   - Scheduled runs (`COMMIT_TRIGGERED_RUN` unset) execute:
     `bazel test ... || echo ...`
   - The `echo` command masks Bazel's failure status
   - GitHub Actions reports success because final command exits 0

**Evidence Cross-Reference:**
- Workflow file condition: `if [[ -z $COMMIT_TRIGGERED_RUN || -z $MAIN_RUN ]]`
- Log observation: "Please run..." message appears in successful jobs
- Exit status verification: Simulated failure returns status 0

**Conclusion:**
The workflow step always exits with status 0 due to the `|| echo` construct. This explains why GitHub Actions reports job success despite Bazel test failures. The exit status of the Bazel command is masked by the subsequent echo command's success.

**Recommended Next Command:**
```bash
# Verify exit status masking in different conditions
bash -c 'false || echo "Masked failure"; echo $?'
```

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
