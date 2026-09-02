# COMMANDS

```
git checkout 50f27d9ef496fe69da6d2969134df6dd2f9aa9b3
# against a cluster with deploy/test-3 already present:
kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=0
```

Expected on older wait semantics: one-shot check, `condition met` if the jsonpath is already populated. Observed on this revision: error requiring `--wait-for-creation` timeout greater than 0.

This packet does not start a cluster. Treat the wait.go excerpt and the command error as the world.
