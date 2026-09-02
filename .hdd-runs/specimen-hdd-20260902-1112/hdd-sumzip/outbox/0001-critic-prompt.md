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

`go mod download` in a module that has no `go.sum` writes checksum lines for `go.mod` files needed by MVS, and does not write checksum lines for the zip content of modules in the build list.

Two identities for `rsc.io/quote v1.5.2`:

```
rsc.io/quote v1.5.2/go.mod h1:…   # go.mod-only
rsc.io/quote v1.5.2 h1:…          # zip content
```

Case A — after `go mod download` with empty `go.sum` (Go 1.15.2 / 1.14.9 / 03a6860):

```
grep '^rsc.io/quote v1.5.2 ' go.sum
```

prints only the `/go.mod` line (or prints nothing for the unsuffixed zip line).

Case B — after `go mod tidy` (or Go 1.16+ `go mod download` that also records zip sums):

```
grep '^rsc.io/quote v1.5.2' go.sum
```

contains both the unsuffixed zip line and the `/go.mod` line.

The checksum database is not consulted for module versions already listed in `go.sum`. A `go.sum` that only has the `/go.mod` identity will not fetch the zip identity from sumdb on a later `go list`.

The developer wants to know which identity `go.sum` actually contained after download: zip content sum, go.mod-only sum, both, or neither.

# OBSERVED

Public golang/go#41341 (jayconrod, 2020-09-11). Failing world: Go 1.15.2, 1.14.9, and commit `03a686069191e3515c7f27f6d90b66d272e0e3a2`. `GOSUMDB=off` in the report; GOPROXY a local module proxy.

Command in a module whose `go.mod` is:

```
module m
go 1.16
require rsc.io/quote v1.5.2
```

with no `go.sum`:

```
go mod download
grep '^rsc.io/quote v1.5.2 ' go.sum
```

Expected: sums for both the `go.mod` files needed by MVS and the content of modules in the build list.

Saw: `go.sum` only contains sums for the `go.mod` files.

The unsuffixed `go.sum` line is the zip/dirhash of module source. The `version/go.mod` line is the hash of that module's go.mod only. `go mod tidy` adds or removes the zip line as needed. Pre-1.16 `go mod download` could leave a build-list module listed only as `/go.mod`.

This packet is an owned two-file fixture of those two `go.sum` identities. It does not include a local Go checkout. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# not executed on this lab host (golang/go#41341 report)
# go version go1.15.2 / 1.14.9 / 03a686069191e3515c7f27f6d90b66d272e0e3a2
# GOSUMDB=off

# case A
rm -f go.sum
go mod download
grep '^rsc.io/quote v1.5.2 ' go.sum
# only rsc.io/quote v1.5.2/go.mod h1:…

# case B
go mod tidy
grep '^rsc.io/quote v1.5.2' go.sum
# rsc.io/quote v1.5.2 h1:…
# rsc.io/quote v1.5.2/go.mod h1:…
```

Owned fixtures in `files/` are the two identities, not a go toolchain run.

local-fixture
  files/go.sum.download
  files/go.sum.tidy

RELEVANT MATERIAL

### go.sum.download

rsc.io/quote v1.5.2/go.mod h1:fixture-quote-mod-only=
rsc.io/sampler v1.3.0/go.mod h1:fixture-sampler-mod-only=
golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:fixture-text-mod-only=

### go.sum.tidy

golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c h1:fixture-text-zip=
golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:fixture-text-mod-only=
rsc.io/quote v1.5.2 h1:fixture-quote-zip=
rsc.io/quote v1.5.2/go.mod h1:fixture-quote-mod-only=
rsc.io/sampler v1.3.0 h1:fixture-sampler-zip=
rsc.io/sampler v1.3.0/go.mod h1:fixture-sampler-mod-only=

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

        ### Field Report: Investigating `go.sum` Identities with `gosum-analyze`

**Situation:**  
We have two fixture files representing `go.sum` states:
- `files/go.sum.download`: Post-`go mod download` state (Go 1.15.2/1.14.9 behavior)
- `files/go.sum.tidy`: Post-`go mod tidy` state (Go 1.16+ behavior)

An unfamiliar CLI tool `gosum-analyze` is present. Documentation is unavailable, so we probe its capabilities through concrete operations.

---

### Operation Log

#### 1. **Tool discovery**  
Ran basic help command to understand usage:  
```bash
gosum-analyze --help
```
**Output:**  
```
Usage: gosum-analyze <command> [options]

Commands:
  inspect   Show entries for a specific module version
  list      List all module versions in go.sum
  diff      Compare two go.sum files
  explain   Describe hash types

Options:
  --file    Path to go.sum file (default: ./go.sum)
```
*Observation:* Tool supports targeted inspection of `go.sum` files.

---

#### 2. **Inspecting `go.sum.download` for `rsc.io/quote v1.5.2`**  
```bash
gosum-analyze inspect --file=files/go.sum.download rsc.io/quote v1.5.2
```
**Output:**  
```
MODULE           VERSION  TYPE   HASH
rsc.io/quote     v1.5.2   mod    h1:fixture-quote-mod-only=
```
*Observation:* Only the `go.mod` checksum (`/go.mod` suffix) is present. No zip content checksum (unsuffixed line). Matches Case A behavior.

---

#### 3. **Inspecting `go.sum.tidy` for same module**  
```bash
gosum-analyze inspect --file=files/go.sum.tidy rsc.io/quote v1.5.2
```
**Output:**  
```
MODULE           VERSION  TYPE   HASH
rsc.io/quote     v1.5.2   zip    h1:fixture-quote-zip=
rsc.io/quote     v1.5.2   mod    h1:fixture-quote-mod-only=
```
*Observation:* Both zip content and `go.mod` checksums present. Matches Case B behavior.

---

#### 4. **Verifying absence of zip checksum in download state**  
Explicitly check for unsuffixed (zip) entry:  
```bash
gosum-analyze inspect --file=files/go.sum.download rsc.io/quote v1.5.2 --type=zip
```
**Output:**  
```
No matching entries found.
```
*Failure:* Tool returns error code 1. Confirms zip checksum is missing in download state.

---

#### 5. **Cross-validating with dependency `golang.org/x/text`**  
```bash
gosum-analyze inspect --file=files/go.sum.download golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c
```
**Output:**  
```
MODULE                   VERSION                          TYPE   HASH
golang.org/x/text        v0.0.0-20170915032832-14c0d48ead0c  mod    h1:fixture-text-mod-only=
```
*Observation:* Consistent pattern – only `go.mod` checksum recorded for transitive dependencies in download state.

---

#### 6. **File comparison**  
```bash
gosum-analyze diff files/go.sum.download files/go.sum.tidy
```
**Output:**  
```
--- files/go.sum.download
+++ files/go.sum.tidy
+ golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c h1:fixture-text-zip=
+ rsc.io/quote v1.5.2 h1:fixture-quote-zip=
+ rsc.io/sampler v1.3.0 h1:fixture-sampler-zip=
```
*Observation:* Confirms `go mod tidy` adds missing zip checksums without altering existing `go.mod` checksums.

---

### Conclusions

1. **Post-`go mod download` (Go ≤1.15):**  
   `go.sum` contains **only `go.mod` checksums** for modules in the build list.  
   *Verified for both direct (`rsc.io/quote`) and transitive (`golang.org/x/text`) dependencies.*

2. **Post-`go mod tidy` (Go 1.16+):**  
   `go.sum` contains **both zip content and `go.mod` checksums**.

3. **Tool validation:**  
   `gosum-analyze` successfully:  
   - Identified checksum types (`mod` vs `zip`)  
   - Detected version-specific entries  
   - Confirmed absence/presence of specific checksum types  
   - Validated behavior across multiple dependencies  

**Answer to developer:**  
After `go mod download` with no prior `go.sum` (Go ≤1.15), `go.sum` contains **only the `/go.mod` checksum** for `rsc.io/quote v1.5.2`. The zip content checksum is added later by `go mod tidy` or equivalent operations.

---

### Artifacts
- Full output logs available in `/ops/logs/gosum-investigation-20231015.txt`
- Fixture files preserved at `files/{go.sum.download, go.sum.tidy}`

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
