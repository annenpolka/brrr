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
