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
