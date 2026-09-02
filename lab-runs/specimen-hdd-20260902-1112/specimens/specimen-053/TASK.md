# TASK

Two specs run in parallel (`turbo_tests`). Both call `with_git_configured`, which writes git credentials to a store file under the working directory.

CI (`common`) fails with:

```
expected: "***private.com\n"
     got: "***github.com\n"
```

`.gitconfig` already used a per-run random suffix. The credential store path did not.

The developer wants to know which file the two processes actually shared, and why one spec could read the other spec's credentials.
