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

A Gradle configuration-cache hit is expected on the second `./gradlew :help --configuration-cache`. Instead the second run stores a new entry:

```
Calculating task graph as configuration cache cannot be reused because system property 'idea.io.use.nio2' has changed.
```

The third run then hits. Nothing in the build script reads `idea.io.use.nio2`. Some plugin or Kotlin-DSL compile path called `System.getProperties()` during configuration.

The developer wants to know which properties entered the configuration-cache identity, and which of those were actually read by configuration.

# OBSERVED

Public gradle/gradle#30145 / PR 38081. Failing world: a configuration-time `System.getProperties()` (or `props.putAll(System.getProperties())`) snapshots every system property into the configuration-cache fingerprint.

Kotlin DSL compilation can set `idea.io.use.nio2` via `setIdeaIoUseFallback` (JetBrains/kotlin `compiler/cli/cli-common/.../environment/util.kt`). Gradle also calls that helper. The property can differ between the first store and the second load even on CI agents with no IDE.

Public second-run log:

```
Calculating task graph as configuration cache cannot be reused because system property 'idea.io.use.nio2' has changed.
```

Third run hits. `help` does not mention the property.

Owned analog `files/cc_unused_prop.py` (host-executed):

```
used_keys path
unused idea.io.use.nio2
all_first <hash> all_second <other> all_same False
used_first <hash> used_second <same> used_same True
invalidate_unused True
```

This packet does not include a local Gradle clone. Do not execute Gradle on this host.

# COMMANDS

```
./gradlew :help --configuration-cache
# second run (failing):
#   cannot be reused because system property 'idea.io.use.nio2' has changed
python3 files/cc_unused_prop.py
```

Not executed on this lab host except the owned analog.

TREE

files/cc_unused_prop.py
files/cc_miss.txt

RELEVANT MATERIAL

### cc_miss.txt

Calculating task graph as configuration cache cannot be reused because system property 'idea.io.use.nio2' has changed.

### cc_unused_prop.py

#!/usr/bin/env python3
"""Owned analog: unused property in a full snapshot invalidates identity."""
import hashlib, json

USED = ("path",)
UNUSED = "idea.io.use.nio2"

def ident(props, mode):
    if mode == "all":
        payload = json.dumps(props, sort_keys=True)
    else:
        payload = json.dumps({k: props[k] for k in USED if k in props}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:12]

def main():
    a = {"path": "/app", UNUSED: "false"}
    b = {"path": "/app", UNUSED: "true"}
    print("used_keys", *USED)
    print("unused", UNUSED)
    print("all_first", ident(a, "all"), "all_second", ident(b, "all"), "all_same", ident(a, "all") == ident(b, "all"))
    print("used_first", ident(a, "used"), "used_second", ident(b, "used"), "used_same", ident(a, "used") == ident(b, "used"))
    print("invalidate_unused", ident(a, "all") != ident(b, "all") and ident(a, "used") == ident(b, "used"))

if __name__ == "__main__":
    main()

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
