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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
