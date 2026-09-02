# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

        CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A large multi-project Gradle build enables Isolated Projects and parallel configuration. Configuration sometimes fails on an arbitrary project with a `HashMap$Node` / `HashMap$TreeNode` ClassCastException inside `BuildScopeInMemoryCachingScriptClassCompiler.compile`.

The same build often succeeds on retry. The stack is in script-class compilation during project configuration, not in task execution.

The developer wants to know which cache is being mutated, which threads reach `compile()`, and why the failure names a project that did not change.

# OBSERVED

Public issue gradle/gradle#38667, checkout `3d2f099490ab5f7d29fc664da6d63f8a432a6273` (PR base / merge parent).

```
A problem occurred configuring project ':services:platform:payment'.
> class java.util.HashMap$Node cannot be cast to class java.util.HashMap$TreeNode

Caused by: java.lang.ClassCastException: class java.util.HashMap$Node cannot be cast to class java.util.HashMap$TreeNode
      at org.gradle.groovy.scripts.internal.BuildScopeInMemoryCachingScriptClassCompiler.compile(BuildScopeInMemoryCachingScriptClassCompiler.java:51)
      at org.gradle.groovy.scripts.DefaultScriptCompilerFactory$ScriptCompilerImpl.compile(DefaultScriptCompilerFactory.java:49)
      at org.gradle.configuration.DefaultScriptPluginFactory$ScriptPluginImpl.apply(DefaultScriptPluginFactory.java:131)
      at org.gradle.configuration.project.BuildScriptProcessor.execute(BuildScriptProcessor.java:46)
```

Flags in play: `org.gradle.configuration-cache.parallel=true` and isolated projects. The named project varies across runs.

On this revision the build-scope cache field is:

```
private final Map<ScriptCacheKey, CompiledScript<?, ?>> cachedCompiledScripts = new HashMap<>();
```

`compile()` does `get` then, on miss, `cache.getOrCompile(...)` then `put`. The wrapped cross-build cache is documented as already safe for concurrent use.

# COMMANDS

```
git checkout 3d2f099490ab5f7d29fc664da6d63f8a432a6273
# user-facing: configure a large Kotlin DSL build with
# org.gradle.configuration-cache.parallel=true
# org.gradle.unsafe.isolated-projects=true
./gradlew help --dry-run
```

A dedicated unit test for this race is not present on the failing revision. This packet does not run Gradle on the host. Treat the stack and the compiler class as the world.

gradle/gradle @ 3d2f099490ab5f7d29fc664da6d63f8a432a6273
  subprojects/core/src/main/java/org/gradle/groovy/scripts/internal/BuildScopeInMemoryCachingScriptClassCompiler.java
  subprojects/core/src/main/java/org/gradle/groovy/scripts/internal/CrossBuildInMemoryCachingScriptClassCache.java

RELEVANT MATERIAL

### subprojects/core/src/main/java/org/gradle/groovy/scripts/internal/BuildScopeInMemoryCachingScriptClassCompiler.java

/*
 * Copyright 2010 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.gradle.groovy.scripts.internal;

import groovy.lang.Script;
import org.codehaus.groovy.ast.ClassNode;
import org.gradle.api.Action;
import org.gradle.api.internal.initialization.ClassLoaderScope;
import org.gradle.groovy.scripts.ScriptSource;
import org.gradle.internal.Cast;

import java.util.HashMap;
import java.util.Map;

/**
 * This in-memory cache is responsible for caching compiled build scripts during a build.
 * If the compiled script is not found in this cache, it will try to find it in the global cache,
 * which will use the delegate script class compiler in case of a miss. The lookup in this cache is
 * more efficient than looking in the global cache, as we do not check the script's hash code here,
 * assuming that it did not change during the build.
 */
public class BuildScopeInMemoryCachingScriptClassCompiler implements ScriptClassCompiler {
    private final CrossBuildInMemoryCachingScriptClassCache cache;
    private final ScriptClassCompiler scriptClassCompiler;
    private final Map<ScriptCacheKey, CompiledScript<?, ?>> cachedCompiledScripts = new HashMap<>();

    public BuildScopeInMemoryCachingScriptClassCompiler(CrossBuildInMemoryCachingScriptClassCache cache, ScriptClassCompiler scriptClassCompiler) {
        this.cache = cache;
        this.scriptClassCompiler = scriptClassCompiler;
    }

    @Override
    public <T extends Script, M> CompiledScript<T, M> compile(ScriptSource source, Class<T> scriptBaseClass, Object target, ClassLoaderScope targetScope, CompileOperation<M> operation, Action<? super ClassNode> verifier) {
        ScriptCacheKey key = new ScriptCacheKey(source.getClassName(), targetScope.getExportClassLoader(), operation.getId());
        CompiledScript<T, M> compiledScript = Cast.uncheckedCast(cachedCompiledScripts.get(key));
        if (compiledScript == null) {
            compiledScript = cache.getOrCompile(target, source, targetScope, operation, scriptBaseClass, verifier, scriptClassCompiler);
            cachedCompiledScripts.put(key, compiledScript);
        }
        return compiledScript;
    }

}

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        Based on the provided material and observed failure, I'll operate within the current environment to investigate the `ClassCastException`. The key observations are:

1. Failure occurs during concurrent access to `cachedCompiledScripts` HashMap
2. Stack trace indicates internal HashMap corruption during treeification
3. Failure is intermittent and affects different projects randomly

**Concrete Investigation Steps:**

1. **Inspect HashMap implementation details:**
```java
// Environment: JDK 8+ (HashMap treeification introduced in 8)
// Check HashMap treeification threshold
System.getProperty("java.version")
// Output: 1.8.0_352 (example)

// Verify treeification parameters
java -Xinternal:java.util.HashMap
// Output: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6 (standard values)
```

2. **Analyze concurrent access patterns:**
```java
// CrossBuildInMemoryCachingScriptClassCache is thread-safe
// But cachedCompiledScripts is plain HashMap with:
//   get() -> null check -> put()
// This is unsafe for concurrent writes

// Reproduce race condition pattern:
import java.util.*;
import java.util.concurrent.*;

public class HashMapRace {
    static Map<Object, Object> map = new HashMap<>();

    public static void main(String[] args) throws Exception {
        ExecutorService exec = Executors.newFixedThreadPool(8);
        for (int i = 0; i < 10000; i++) {
            final Object key = i % 100; // force collisions
            exec.submit(() -> {
                if (map.get(key) == null) {
                    map.put(key, new Object());
                }
            });
        }
        exec.shutdown();
        exec.awaitTermination(1, TimeUnit.MINUTES);
    }
}
// Run multiple times:
java HashMapRace
// Output (occasional failure):
// Exception: java.lang.ClassCastException: java.util.HashMap$Node cannot be cast to java.util.HashMap$TreeNode
```

3. **Confirm unsafe publication:**
```java
// The cachedCompiledScripts field lacks volatile/atomic guarantees
Field cacheField = BuildScopeInMemoryCachingScriptClassCompiler.class.getDeclaredField("cachedCompiledScripts");
cacheField.isAccessible();
Modifier.isVolatile(cacheField.getModifiers()); // Output: false
```

4. **Verify failure matches observed stack:**
```java
// The failing line matches source:
BuildScopeInMemoryCachingScriptClassCompiler.java:51
// Corresponds to: cachedCompiledScripts.put(key, compiledScript)
```

**Findings from Investigation:**

1. **Root Cause:** The `cachedCompiledScripts` HashMap is being concurrently modified by multiple configuration threads when:
   - Bucket collision count exceeds 8 (triggering treeification)
   - Concurrent put() operations occur during tree restructuring
   - Results in corrupt internal structure (Node vs TreeNode mismatch)

2. **Why intermittent?** Depends on:
   - Random project configuration order
   - Hash collisions for ScriptCacheKey
   - Precise thread timing during treeification
   - JVM memory layout differences between runs

3. **Why unaffected projects?** The corruption:
   - Doesn't necessarily affect the key being inserted
   - Can poison any bucket in the map
   - Manifests later during subsequent map operations

**Recommended Fix Path:**

```java
// Replace HashMap with ConcurrentHashMap
private final Map<ScriptCacheKey, CompiledScript<?, ?>> cachedCompiledScripts = new ConcurrentHashMap<>();

// Use atomic computeIfAbsent
compiledScript = cachedCompiledScripts.computeIfAbsent(key, k -> 
    cache.getOrCompile(...)
);
```

**Verification Strategy:**

1. **Stress test with concurrent load:**
```bash
./gradlew help --dry-run --max-workers=16
# Repeat 50x with different worker counts
```

2. **Monitor map internals (add debug):**
```java
// Add before put():
if (cachedCompiledScripts instanceof HashMap) {
    int bins = 0, trees = 0;
    for (Node<?> bin : table) {
        if (bin instanceof TreeNode) trees++;
        else if (bin != null) bins++;
    }
    log.debug("HashMap state: {} bins, {} trees", bins, trees);
}
```

**Final Observation:** The race condition is confirmed through code inspection and reproduction. The fix requires making `cachedCompiledScripts` thread-safe using concurrent collection primitives. The intermittent nature and random project attribution are characteristic of HashMap corruption during concurrent treeification.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
