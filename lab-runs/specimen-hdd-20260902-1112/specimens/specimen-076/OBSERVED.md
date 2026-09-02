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
