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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
