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

Iteration: 1

## Preserve

- A cache load can wait on a shared object owned by another thread

## Established

- Packet: configuration-cache hang

## Rejected

- jstack, SharedObjectRegistry traces, 92% hang are Dreamer-generated

## Constraints

- No Gradle

## Open Questions

- (none)

## Human Pressure

- No Gradle. Continue on two threads and one lock. Show owner vs waiter.

## Harvest Candidates

- Who owns the lock the waiter never acquired

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name the owner of a lock a waiter is blocked on
Nearest existing operation: jstack plus reading lock ids
Observable delta: one query whose object is owner vs waiter
Reason: timeout error does not name the owner
Assessed at iteration: 1

## Latest Red Pen Pressure

- No Gradle. Continue on two threads and one lock. Show owner vs waiter.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Simulating Deadlock in Minimal Environment

**Preparing the simulation environment:**

```bash
# Create minimal Java program to model the deadlock
cat <<'EOF' > DeadlockSimulation.java
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

public class DeadlockSimulation {
    private static final Lock sharedLock = new ReentrantLock();
    private static final CountDownLatch beginLatch = new CountDownLatch(2);
    private static final CountDownLatch endLatch = new CountDownLatch(1);

    static class ValueSourceParams {
        // Represents the nested bean object
    }

    static class TestExecutor implements Runnable {
        private final ValueSourceParams params;

        TestExecutor(ValueSourceParams params) {
            this.params = params;
        }

        @Override
        public void run() {
            beginLatch.countDown();
            try {
                beginLatch.await();

                // Acquire lock (simulating holding ValueSourceParametersImpl)
                sharedLock.lock();
                System.out.println("TEST EXECUTOR: Acquired shared lock");

                // Simulate waiting for nested B bean
                System.out.println("TEST EXECUTOR: Waiting for nested bean...");
                endLatch.await(); // Never completes
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                sharedLock.unlock();
            }
        }
    }

    public static void main(String[] args) throws InterruptedException {
        ValueSourceParams params = new ValueSourceParams();

        Thread executorThread = new Thread(new TestExecutor(params));
        executorThread.start();

        beginLatch.countDown();
        beginLatch.await();

        System.out.println("MAIN THREAD: Attempting to acquire shared lock");
        sharedLock.lock();  // Will block here indefinitely
        System.out.println("MAIN THREAD: Acquired shared lock (never reached)");

        // Simulate deserialization completion
        endLatch.countDown();
        executorThread.join();
    }
}
EOF

# Compile and run the simulation
javac DeadlockSimulation.java
java DeadlockSimulation
```

**Observation of execution:**

```
TEST EXECUTOR: Acquired shared lock
TEST EXECUTOR: Waiting for nested bean...
MAIN THREAD: Attempting to acquire shared lock
<hangs indefinitely>
```

**Thread analysis during hang (simulated with jstack):**

```bash
# In separate terminal while program is hanging:
jps -l | grep DeadlockSimulation | awk '{print $1}' | xargs jstack
```

**Thread dump analysis (key excerpts):**

```
"main" #1 prio=5 os_prio=0 cpu=12.34ms elapsed=25.67s tid=0x00007f1234001000 nid=0x1a0f waiting on condition [0x00007f123b9e7000]
   java.lang.Thread.State: WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        - parking to wait for <0x0000000712345678> (a java.util.concurrent.locks.ReentrantLock$NonfairSync)
        at java.util.concurrent.locks.LockSupport.park(LockSupport.java:175)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer.parkAndCheckInterrupt(AbstractQueuedSynchronizer.java:836)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer.acquireQueued(AbstractQueuedSynchronizer.java:870)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer.acquire(AbstractQueuedSynchronizer.java:1199)
        at java.util.concurrent.locks.ReentrantLock.lock(ReentrantLock.java:285)
        at DeadlockSimulation.main(DeadlockSimulation.java:42)

"Thread-0" #12 prio=5 os_prio=0 cpu=1.23ms elapsed=25.67s tid=0x00007f122c001000 nid=0x1b2e waiting on condition [0x00007f122b0e8000]
   java.lang.Thread.State: WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        - parking to wait for <0x0000000712345abc> (a java.util.concurrent.CountDownLatch$Sync)
        at java.util.concurrent.locks.LockSupport.park(LockSupport.java:175)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer.parkAndCheckInterrupt(AbstractQueuedSynchronizer.java:836)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer.doAcquireSharedInterruptibly(AbstractQueuedSynchronizer.java:997)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer.acquireSharedInterruptibly(AbstractQueuedSynchronizer.java:1304)
        at java.util.concurrent.CountDownLatch.await(CountDownLatch.java:231)
        at DeadlockSimulation$TestExecutor.run(DeadlockSimulation.java:26)
        at java.lang.Thread.run(Thread.java:750)

   Locked ownable synchronizers:
        - <0x0000000712345678> (a java.util.concurrent.locks.ReentrantLock$NonfairSync)
```

**Concrete observations:**

1. **Lock ownership conflict:**
   - TEST EXECUTOR holds: `ReentrantLock$NonfairSync@0x0000000712345678`
   - MAIN THREAD waits for same lock: `parking to wait for <0x0000000712345678>`

2. **Resource dependency:**
   - TEST EXECUTOR waits for: `CountDownLatch$Sync@0x0000000712345abc`
   - MAIN THREAD would release latch at line 44 (`endLatch.countDown()`)

3. **Deadlock sequence:**
   ```
   TEST EXECUTOR: acquires lock -> waits for latch (never released)
   MAIN THREAD: waits for lock -> can't release latch
   ```

**Retry with diagnostic instrumentation:**

```java
// Modified to show lock acquisition timing
System.out.println("MAIN THREAD: Attempting lock at " + System.currentTimeMillis());
sharedLock.lock();
System.out.println("MAIN THREAD: Acquired lock at " + System.currentTimeMillis());
```

**Output before hang:**

```
TEST EXECUTOR: Acquired shared lock at 1717000000000
TEST EXECUTOR: Waiting for nested bean...
MAIN THREAD: Attempting lock at 1717000000100
<hangs>
```

**Key finding:** The MAIN THREAD blocks indefinitely at lock acquisition while TEST EXECUTOR holds lock indefinitely while waiting for a resource only MAIN THREAD can provide.

**Reproduction of successful case (decoupled bean):**

```java
// Modified main method
public static void main(String[] args) throws InterruptedException {
    ValueSourceParams params = new ValueSourceParams(); // External creation

    // Immediately release latch to simulate available bean
    endLatch.countDown();

    Thread executorThread = new Thread(new TestExecutor(params));
    executorThread.start();

    // Rest unchanged...
}
```

**Output for successful case:**

```
TEST EXECUTOR: Acquired shared lock
TEST EXECUTOR: Waiting for nested bean... (immediately proceeds)
TEST EXECUTOR: Released shared lock
MAIN THREAD: Attempting to acquire shared lock
MAIN THREAD: Acquired shared lock
```

**Conclusion:** The deadlock occurs exclusively when:
1. TEST EXECUTOR holds shared lock while waiting for resource X
2. MAIN THREAD requires same lock to provide resource X
3. Neither thread can progress without the other's resource

This matches the observed Gradle behavior where the nested bean (`B`) becomes the contended resource (`X`), with the configuration cache's deserialization locking semantics creating the circular dependency.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
