# HDD Ledger

Iteration: 2

## Preserve

- A plain HashMap cache can corrupt under concurrent compile() during parallel configuration
- The failure can name a project that did not change
- A shared unsynchronized map can fail only under concurrent writers
- A structure safe sequentially can be racy with two writers

## Established

- Packet: Isolated Projects + parallel configuration; intermittent ClassCastException Node vs TreeNode in BuildScopeInMemoryCachingScriptClassCompiler.compile
- Packet: Gradle cachedCompiledScripts HashMap race
- Packet: unsynchronized HashMap

## Rejected

- java HashMapRace transcripts and field-volatile checks are not host evidence
- A recommended ConcurrentHashMap / computeIfAbsent patch is a Dreamer repair, not a specimen observation
- java -Xinternal and specific JDK 1.8.0_352 are unsupported precision
- HashMapTest.java transcripts are Dreamer-generated

## Constraints

- No Gradle checkout, no ./gradlew
- An owned concurrent map fixture with colliding keys is the world
- No Gradle
- An owned threading fixture is the world
- Ground with threading + dict, not Gradle

## Open Questions

- (none)

## Human Pressure

- No Gradle. Continue on a tiny unsynchronized dict written from two threads.

## Harvest Candidates

- Ask which cache is mutated, which threads reach compile(), and why the failure names an unchanged project
- Ask which shared structure is written without exclusion
- Which shared structure is written without exclusion

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a shared structure written without exclusion
Nearest existing operation: read the map field and the lock
Observable delta: missing exclusion as the object
Reason: crash stacks do not name the missing lock
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
