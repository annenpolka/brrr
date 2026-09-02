KNOWN FIX (sealed): kubernetes/kubernetes#125630 merge da479a82ebb6d4117b69f2c78364c81a513ad511, reverting #122994's wait-for-creation default.

#122994 made WaitForCreation default true so missing objects would be waited on. Combined with Timeout==0 that path returned `--wait-for-creation requires a timeout value greater than 0`, breaking the documented one-shot check.

Repair: drop WaitForCreation from flags/options, restore RunWait to visit immediately, add wait.sh coverage for `kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=0` expecting `condition met` on an existing deployment.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
