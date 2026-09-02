CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A wait command documents timeout 0 as check once. With wait-for-creation default true, timeout 0 aborts before looking at the object. Disabling wait-for-creation, or using for=delete, restores the one-shot visit.

The developer wants to know whether the object was visited.

# OBSERVED

Owned flag records (no cluster):

timeout=0 wait_for_creation=true for=jsonpath object_exists=true → abort wait-for-creation-requires-timeout, visited false
timeout=0 wait_for_creation=false for=jsonpath object_exists=true → oneshot visit
timeout=0 wait_for_creation=true for=delete object_exists=true → oneshot visit

# COMMANDS

See waitoneshot CLI. Not kubectl.

flags only

RELEVANT MATERIAL

### flags.txt

timeout=0 wait_for_creation=true for=jsonpath exists=true

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
