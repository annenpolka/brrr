# OBSERVED

Public kubernetes/kubernetes#125630 (revert of behavior from #122994) on failing merge parent `50f27d9ef496fe69da6d2969134df6dd2f9aa9b3`.

Flag help still says: `Zero means check once and don't wait, negative means wait for a week.`

On this revision `NewWaitFlags` sets `WaitForCreation: true` by default. `RunWait` begins with:

```
if o.WaitForCreation && o.Timeout == 0 {
    return fmt.Errorf("--wait-for-creation requires a timeout value greater than 0")
}
```

So `--timeout=0` errors before the condition function runs, even when the object already exists.

`--wait-for-creation` help: `The default value is true. If set to true, also wait for creation of objects if they do not already exist. This flag is ignored in --for=delete`.

#122994 release note (later cleared): `kubectl wait` will now wait for resources to be created by default.
