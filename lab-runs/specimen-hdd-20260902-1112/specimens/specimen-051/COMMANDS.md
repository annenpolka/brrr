# COMMANDS

```
./gradlew show --configuration-cache
./gradlew show --configuration-cache   # second run: load hangs / times out on failing revision
```

Focused in-tree names on the PR:

```
:configuration-cache:embeddedIntegTest --tests org.gradle.internal.cc.impl.ConfigurationCacheValueSourceIntegrationTest
```

Not executed on the lab host. Treat the snippets and timeout as the world.
