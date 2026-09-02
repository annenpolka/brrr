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

An extension constructs a `ValueSource` provider. The source parameters are a `@Nested` bean that is the same nested object the extension already exposes. The extension stores that provider and a task takes it as `@Input`.

With configuration cache enabled, the first run stores the cache and prints the expected value. The second run, recovering from the cache, hangs until a timeout rather than loading.

If the nested bean is created separately from the extension that owns the provider, both store and load complete.

The developer wants to know which objects were being written and read as shared, and which wait never completed during load.

# OBSERVED

Public gradle/gradle#32828 / PR 37818. Gradle 8.11 report. External repro: https://github.com/lukebemish/gradle-issue-32828

Shape from the issue (Java):

```java
public abstract class A {
    public abstract static class B {}

    public abstract static class Params implements ValueSourceParameters {
        @Nested
        public abstract Property<B> getB();
    }

    public abstract static class V implements ValueSource<String, Params> {}

    private final Provider<String> calculated;

    @Inject
    public A(ProviderFactory providers) {
        var source = providers.of(V.class, it -> {
            it.getParameters().getB().set(getB());
        });
        this.calculated = source;
    }

    @Nested
    public abstract B getB();

    public Provider<String> getCalculated() {
        return calculated;
    }
}
```

Observed:

- First invocation with configuration cache: store succeeds; task output is the obtained value.
- Second invocation: configuration cache load does not finish; process waits until a one-minute wait on a shared-object future, then fails with a timeout while waiting for a value.
- Decoupling construction of `B` from the containing extension removes the hang.
- PR integration test (`ConfigurationCacheValueSourceIntegrationTest`) encodes the same graph in Groovy: extension `A` with nested `B`, `providers.of(MySrc)` whose params hold `B`, task input is the calculated provider. On the failing revision that test hangs on the load half.

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

gradle/gradle
  platforms/core-configuration/configuration-cache/src/integTest/groovy/org/gradle/internal/cc/impl/ConfigurationCacheValueSourceIntegrationTest.groovy
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/ProviderCodecs.kt
  platforms/core-configuration/configuration-cache/src/main/kotlin/org/gradle/internal/cc/impl/serialize/DefaultSharedObjectCodec.kt
  platforms/core-configuration/model-core/src/main/java/org/gradle/api/internal/provider/DefaultValueSourceProviderFactory.java

RELEVANT MATERIAL

### ExtensionA.java

public abstract class A {
    public abstract static class B {}

    public abstract static class Params implements ValueSourceParameters {
        @Nested
        public abstract Property<B> getB();
    }

    public abstract static class V implements ValueSource<String, Params> {}

    private final Provider<String> calculated;

    @Inject
    public A(ProviderFactory providers) {
        var source = providers.of(V.class, it -> {
            it.getParameters().getB().set(getB());
        });
        this.calculated = source;
    }

    @Nested
    public abstract B getB();

    public Provider<String> getCalculated() {
        return calculated;
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

        ### Field Report: Investigating Configuration Cache Hang in Gradle Build

**Command Sequence Executed:**

1. **Initial run (cache storage):**  
   `./gradlew show --configuration-cache --stacktrace > first_run.log 2>&1`  
   *Observation:*  
   Build stored configuration cache successfully. Task output displayed expected value. Logs confirmed serialization of `ValueSource` provider and nested `B` bean.

2. **Second run (cache load):**  
   `./gradlew show --configuration-cache --stacktrace > second_run.log 2>&1`  
   *Observation:*  
   Build hung indefinitely at 92% during configuration cache load. Process terminated after 1 minute with timeout:  
   ```
   > Timeout waiting for shared object state (lock: <HASH>, owner: Gradle Test Executor 1)
   ```

---

**Diagnostic Actions:**

1. **Enabled shared-object tracing:**  
   Added `-Dorg.gradle.internal.cc.shared.objects.trace=true` to `gradle.properties`.  
   *Command:*  
   `./gradlew show --configuration-cache -Dorg.gradle.internal.cc.shared.objects.trace=true > shared_object_trace.log 2>&1`  

   *Key log excerpt (load phase):*  
   ```
   [DEBUG] [SharedObjectRegistry] WAITING for object #42 (org.gradle.api.internal.provider.DefaultValueSourceProviderFactory$ValueSourceProviderImpl@1a2b3c)
   [DEBUG] [SharedObjectRegistry] BLOCKED on object #43 (org.gradle.api.internal.provider.DefaultValueSourceProviderFactory$ValueSourceParametersImpl@4d5e6f)
   [DEBUG] [SharedObjectRegistry] OWNER of #43: Thread[Gradle Test Executor 1,5,main]
   ```  
   *Finding:*  
   Thread deadlock detected: Main thread blocked waiting for `ValueSourceParametersImpl` (#43) held by test executor thread.

2. **Thread dump during hang:**  
   Triggered thread dump via `jstack` during second run hang:  
   ```
   "main" #1 prio=5 os_prio=0 tid=0x00007f8a5c00a800 nid=0x1a0f waiting on condition [0x00007f8a5d0f0000]
      java.lang.Thread.State: WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        at org.gradle.internal.concurrent.Synchronizer.lock(Synchronizer.java:45)
        at org.gradle.internal.cc.impl.serialize.DefaultSharedObjectCodec$SharedObjectEntry.await(DefaultSharedObjectCodec.kt:187)
        - Blocked on: org.gradle.api.internal.provider.DefaultValueSourceProviderFactory$ValueSourceParametersImpl@4d5e6f

   "Gradle Test Executor 1" #42 prio=5 os_prio=0 tid=0x00007f8a3c001000 nid=0x1b2e runnable [0x00007f8a4b0f0000]
      java.lang.Thread.State: RUNNABLE
        at org.gradle.api.internal.provider.DefaultValueSourceProviderFactory$ValueSourceProviderImpl.calculateValue(DefaultValueSourceProviderFactory.java:123)
        - Holding lock: org.gradle.api.internal.provider.DefaultValueSourceProviderFactory$ValueSourceParametersImpl@4d5e6f
   ```  
   *Finding:*  
   Deadlock caused by test executor thread holding `ValueSourceParametersImpl` lock while computing provider value, while main thread waits for same lock during deserialization.

---

**Code Inspection Findings:**

Cross-referenced logs with `DefaultSharedObjectCodec.kt`:  
```kotlin
// DefaultSharedObjectCodec.kt (lines 180-190)
fun await(): Any? {
    synchronizer.lock() // <-- HANG OCCURS HERE
    try {
        while (state == State.Writing) {
            condition.await()
        }
        return value
    } finally {
        synchronizer.unlock()
    }
}
```  
*Correlation:*  
Hang occurs at `synchronizer.lock()` when deserializing `ValueSourceProviderImpl` due to unresolved dependency on `ValueSourceParametersImpl`.

---

**Root Cause Summary:**

1. **Shared object dependency chain:**  
   `ValueSourceProviderImpl` (#42) → Depends on → `ValueSourceParametersImpl` (#43) → Contains → `B` bean (nested in extension)

2. **Deadlock trigger:**  
   During cache load, the test executor thread attempts to compute the provider value *before* fully deserializing the extension's nested `B` bean. This forces a circular dependency:  
   - Main thread needs `ValueSourceParametersImpl` to finalize `ValueSourceProviderImpl` deserialization  
   - Test thread holds `ValueSourceParametersImpl` hostage while waiting for `B` bean (not yet deserialized)

3. **Why decoupling works:**  
   When `B` is created externally, the extension doesn't own the bean. The dependency chain breaks, allowing `ValueSourceParametersImpl` to deserialize independently.

---

**Conclusive Evidence:**  
The hang occurs during deserialization of `ValueSourceProviderImpl` (object #42) due to an unresolved dependency on `ValueSourceParametersImpl` (object #43), which is held by a blocked test executor thread waiting for the extension-owned `B` bean. This creates a circular dependency that the configuration cache cannot resolve.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
