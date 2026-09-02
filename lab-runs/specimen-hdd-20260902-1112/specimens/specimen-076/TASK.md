# TASK

A Gradle configuration-cache hit is expected on the second `./gradlew :help --configuration-cache`. Instead the second run stores a new entry:

```
Calculating task graph as configuration cache cannot be reused because system property 'idea.io.use.nio2' has changed.
```

The third run then hits. Nothing in the build script reads `idea.io.use.nio2`. Some plugin or Kotlin-DSL compile path called `System.getProperties()` during configuration.

The developer wants to know which properties entered the configuration-cache identity, and which of those were actually read by configuration.
