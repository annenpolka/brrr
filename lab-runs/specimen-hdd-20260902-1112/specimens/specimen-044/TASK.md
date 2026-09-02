# TASK

`kubectl wait` documents `--timeout` as: zero means check once and do not wait. After a recent change, waiting on an already-existing Deployment with `--timeout=0` does not perform that one-shot check.

A typical invocation:

```
kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=0
```

returns an error about `--wait-for-creation` instead of `deployment.apps/test-3 condition met` (or a one-shot condition failure).

The developer wants to know which default now governs timeout 0, whether the object is even visited, and how that interacts with the flag help text.
