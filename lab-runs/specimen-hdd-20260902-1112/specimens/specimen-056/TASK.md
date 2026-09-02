# TASK

A wait command documents timeout 0 as check once. With wait-for-creation default true, timeout 0 aborts before looking at the object. Disabling wait-for-creation, or using for=delete, restores the one-shot visit.

The developer wants to know whether the object was visited.
