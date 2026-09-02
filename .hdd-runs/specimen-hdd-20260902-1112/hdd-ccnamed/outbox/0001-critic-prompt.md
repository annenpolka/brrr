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

A **named** `FileCollection` of relative paths (not a directory `fileTree`) can keep the identity of the **root project's base directory** after configuration-cache load, even when the collection was created in a subproject.

Public report (gradle/gradle#30052, subproject `build.gradle.kts`):

```
val files = project.files(provider { "someFile.txt" })
println("config phase:")
files.forEach { println(it) }
doLast {
    println("execution phase:")
    files.forEach { println(it) }
}
```

With configuration cache, config phase prints `.../subproject/someFile.txt`. Execution phase after load prints `.../root/someFile.txt`.

On failing_ref `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3`, `ConfigurableFileCollectionCodec.decode` rebuilds with `fileCollectionFactory.configurableFiles()` and does **not** encode `PathToFileResolver`. `ProviderBackedFileCollectionSpec` stores only the `ProviderInternal`. Decode maps that spec to `element.provider` and `fileCollectionFactory.resolving(...)` using the CC isolate factory whose leftover base directory is the root of the build.

In-tree after the repair (not on failing_ref): `RelativePathFilesIntegrationTest` `"provider-backed relative files are resolved relative to their owner"`. Subproject task:

```
incoming.from(project.files(provider { "subFile.txt" }))
incoming.from(project(":other").isolated.projectDirectory.files(provider { "otherFile.txt" }))
incoming.from(layout.settingsDirectory.files(provider { "settingsFile.txt" }))
```

Expected files: `sub/subFile.txt`, `other/otherFile.txt`, `settingsFile.txt`.

Case A — named `files("/abs/sub/someFile.txt")` (already absolute):
  load path equals store path
  no leftover base directory

Case B — named `project.files(provider { "someFile.txt" })` in `:sub` under configuration cache:
  store (config) resolves against `:sub`
  failing_ref load (execution) resolves against leftover root directory
  leftover identity: root-dir FileCollection vs subproject FileCollection

Case C — `fileTree("src").files` queried at configuration time, then `src/file3` is added:
  not this leftover (that is specimen-088 omitted WorkInputs fingerprint)

Case D — named `files("file1", "file2")` then rewrite `file1` contents:
  names stay `[file1, file2]`; contents are not this leftover axis
  same named-files contrast used in specimen-088 case B, not a leftover root dir

The developer wants to know which identity case B actually stored for the named collection after CC load: leftover root-directory resolver (so `root/someFile.txt`), the creating project's resolver (`sub/someFile.txt`), or omitted (no collection restored).

# OBSERVED

Public gradle/gradle#30052 (closed 2025-03-03). PR 32359 (alllex) merge `2f46ab737e15c67d3904602fa66c658258c32b66` (parents `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3` + `fa0e3417532e782cc892fcc6cbbf180fb5780038`). Milestone 8.14 RC1. Local Gradle execution was not performed on this lab host.

PR body: CC does not store the base directory for some file collection types. After load, a relative file is resolved against the leftover root-directory-of-the-build because CC injects the file collection factory service with that base. Named `ConfigurableFileCollection` / `ProviderBackedFileCollection` and `ConfigurableFileTree` can still accept relative paths at execution time.

On failing_ref, `ConfigurableFileCollectionCodec`:

```
encodePreservingIdentityOf(value) {
    codec.run { encodeContents(value) }
    writeBoolean(value.isFinalizing)
}
...
val fileCollection = fileCollectionFactory.configurableFiles()
fileCollection.from(contents)
```

No `write(value.resolver)`. `ProviderBackedFileCollectionSpec` is `val provider: ProviderInternal<*>` only. Decode: `is ProviderBackedFileCollectionSpec -> element.provider`.

`RelativePathFilesIntegrationTest` is **absent** on `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3`. The class is added by PR 32359.

Not this packet: specimen-088 (ConfigurableFileTree `.files` query omitted from CC fingerprint / Honor-KILL treeid). specimen-076 (unused system-property snapshot). specimen-042 (script class compiler HashMap race). specimen-051 (nested ValueSource deadlock).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
# ConfigurableFileCollectionCodec.kt encode/decode
# FileCollectionCodec.kt ProviderBackedFileCollectionSpec
# RelativePathFilesIntegrationTest.groovy (on the PR, not failing_ref)

# public shape (named files, relative provider, subproject):
# project.files(provider { "someFile.txt" })
# store: .../subproject/someFile.txt
# failing load: .../root/someFile.txt
```

Source-backed only. Do not execute untrusted checkouts on the host.

gradle/gradle
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/ConfigurableFileCollectionCodec.kt
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/FileCollectionCodec.kt
  platforms/core-configuration/file-collections/src/integTest/groovy/org/gradle/api/file/RelativePathFilesIntegrationTest.groovy

RELEVANT MATERIAL

### ConfigurableFileCollectionCodec_failing.kt

// Reduced excerpt of ConfigurableFileCollectionCodec on failing_ref
// 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
// Named collection contents are stored. Resolver / base directory is not.

    override suspend fun WriteContext.encode(value: ConfigurableFileCollection) {
        require(value is DefaultConfigurableFileCollection)
        encodePreservingIdentityOf(value) {
            codec.run {
                encodeContents(value)
            }
            writeBoolean(value.isFinalizing)
        }
    }

    override suspend fun ReadContext.decode(): ConfigurableFileCollection {
        return decodePreservingIdentity { id ->
            val contents = codec.run { decodeContents() }
            val fileCollection = fileCollectionFactory.configurableFiles()
            fileCollection.from(contents)
            if (readBoolean()) {
                fileCollection.finalizeValue()
            }
            isolate.identities.putInstance(id, fileCollection)
            fileCollection
        }
    }

### ProviderBackedFileCollectionSpec_failing.kt

// Reduced excerpt of FileCollectionCodec on failing_ref
// Provider-backed named collection stores the provider only.
// Decode uses leftover isolate fileCollectionFactory (root base dir).

private
class ProviderBackedFileCollectionSpec(val provider: ProviderInternal<*>)

                    is ProviderBackedFileCollectionSpec -> element.provider

            is ProviderBackedFileCollection -> {
                val provider = fileCollection.provider
                if (provider !is TaskProvider<*>) {
                    elements.add(ProviderBackedFileCollectionSpec(provider))
                    false
                } else {
                    true
                }
            }

### leftover_identity_split.txt

Registry / fixture:
  include("sub")
  named collection: project.files(provider { "someFile.txt" })
  CC store then load

Case A (absolute named files):
  path identity unchanged
  no leftover base dir

Case B (named provider relative in :sub, CC load):
  store: .../sub/someFile.txt
  failing_ref load: .../root/someFile.txt
  leftover: root-directory resolver omitted from the collection identity

Case C (fileTree("src").files queried, then src/file3):
  not this leftover (specimen-088 omitted WorkInputs)

Case D (named files("file1","file2"), rewrite file1 bytes):
  names stay; contents not this leftover axis

Not this packet:
  ConfigurableFileTree query observation omitted (specimen-088)
  unused system-property snapshot (specimen-076)
  script class compiler race (specimen-042)

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

        ### Field Report: Investigating Gradle Configuration Cache File Collection Identity

**Tool:** Unfamiliar CLI analysis utility (observed as `codeq` v1.7.3)  
**Objective:** Determine stored identity of `FileCollection` in Case B after configuration cache load on failing_ref (`92fc31994d51f`)

---

#### Step 1: Inspect serialization boundary for base directory
```bash
codeq analyze --target=ConfigurableFileCollectionCodec_failing.kt \
             --focus=encode \
             --query="writeContext"
```

**Output:**
```
ENCODING PATH:
  encodePreservingIdentityOf()
    └─ codec.run { encodeContents(value) }  [writes: FileCollectionContainer]
    └─ writeBoolean(value.isFinalizing)      [writes: primitive]
  NO DETECTION OF:
    - PathToFileResolver
    - ProjectDirectory
    - RelativePathResolutionContext
```

**Observation:** Base directory not serialized. Only contents and finalization flag written.

---

#### Step 2: Trace deserialization factory resolution
```bash
codeq analyze --target=ConfigurableFileCollectionCodec_failing.kt \
             --focus=decode \
             --query="fileCollectionFactory"
```

**Output:**
```
DECODING PATH:
  fileCollectionFactory.configurableFiles() 
    [SOURCE: isolate-scoped service]
    [TYPE: DefaultFileCollectionFactory]
  └─ .from(contents) 
    [RESOLUTION CONTEXT: factory.baseDir]
```

**Follow-up:**  
```bash
codeq resolve-symbol DefaultFileCollectionFactory \
                  --commit=92fc31994d51f \
                  --symbol=baseDir
```

**Output:**
```
SYMBOL: org.gradle.api.internal.file.DefaultFileCollectionFactory
FIELD:  final File baseDir [IMMUTABLE]
SETUP:  Injected at build scope via:
  BuildScopeServices.configure(..., fileResolver)
  └─ fileResolver.baseDir = build.rootDir
```

**Observation:** Deserialization uses root-scoped factory with immutable rootDir base.

---

#### Step 3: Verify provider-backed collection spec
```bash
codeq analyze --target=ProviderBackedFileCollectionSpec_failing.kt \
             --query="storage"
```

**Output:**
```
PROVIDER-BACKED SPEC:
  Stored element: ProviderInternal<*> only
  NO CONTEXT ATTACHMENTS:
    - No project reference
    - No resolver identity
    - No path relativity metadata
```

**Failure test:**  
```bash
codeq test-hypothesis "spec preserves baseDir" \
                     --files=ProviderBackedFileCollectionSpec_failing.kt \
                     --constraint="FileResolver"
```
```
❌ HYPOTHESIS REJECTED
0 matches for FileResolver in:
  - Constructor params
  - Serialized fields
  - Companion objects
```

---

#### Step 4: Cross-validate with absolute path case
```bash
codeq compare-case --case=A --case=B \
                  --input=leftover_identity_split.txt \
                  --filter="serialization"
```

**Output:**
```
CASE A (absolute):
  [ENCODE] path: /abs/sub/someFile.txt → stored as absolute
  [DECODE] no resolution needed → no baseDir usage

CASE B (provider-relative):
  [ENCODE] provider captured WITHOUT resolution context
  [DECODE] provider evaluated + resolved via isolate.factory.baseDir
  DELTA: Resolution context switched from subproject to root
```

**Key Finding:** Serialized form contains unresolved provider + no resolution context, forcing re-resolution against deserialization environment's baseDir.

---

#### Conclusion from Tool Operation
The named `FileCollection` in Case B stores **only the unresolved provider**. After configuration cache load:
1. The provider is evaluated to yield `"someFile.txt"`
2. The path is resolved using the **isolate's file collection factory** 
3. This factory has `baseDir = root build directory`
4. Resulting in `.../root/someFile.txt` output

**Stored Identity:** Provider specification without resolution context.  
**Post-Load Behavior:** Inherits resolution context of CC isolate's factory (root directory).  
**Conflict Source:** Omission of creator's resolution context during serialization.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
