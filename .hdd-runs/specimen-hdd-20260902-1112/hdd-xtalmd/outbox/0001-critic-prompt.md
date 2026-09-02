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

Crystal's interpreter can keep the identity of a **previous multidispatch chain** after intervening code instantiates a new concrete type that should have been part of the dispatch, because the cache key hashed `(obj_type, call_signature)` and omitted the resolved `target_def` object IDs.

On failing_ref `c9e867a6703979d8e09abd2a3c1d9a7d55ae945d`:

```
record MultidispatchKey, obj_type : Type, call_signature : CallSignature

cache_key = Context::MultidispatchKey.new(obj_type, signature)
cached_def = context.multidispatchs[cache_key]?
return cached_def if cached_def
```

Two call sites that look identical by that key can resolve to different `target_defs` once a new type lands inside the union. The second site reuses the first's leftover chain; the new type matches none of the branches and execution falls through into `raise "unreachable"`.

Public report (crystal-lang/crystal#16810). `v1 = G(M2 | C).new.as(V); v1.my_check` then `v2 = G(C).new.as(V); v2.my_check`. Expected: second call builds a 5-def chain. Actual: leftover 4-def chain, "Reached the unreachable".

In-tree after the repair (not on failing_ref): `target_def_ids` (sorted object IDs) is part of `MultidispatchKey`.

Case A — second call, no intervening new type:
  cache identity is current
  not leftover-after-new-type

Case B — intervening instantiation, leftover chain:
  leftover: previous multidispatch of the first site
  same (obj_type, signature) vs omitted target_defs
  new concrete type present

Case C — interpreter restart / empty multidispatchs:
  fresh chain
  not leftover previous defs

Case D — key includes target_def_ids (post-repair shape, not on failing_ref):
  new chain after the resolved set changes
  not leftover previous chain

The developer wants to know which identity case B actually used for the second `my_check`: leftover previous-chain (target_defs omitted from the key), current resolved set, or omitted (no cache).

# OBSERVED

Public crystal-lang/crystal#16810. PR 16958 squash `ac82b6ba7dcdc83f72199e8827f68417d61b88c4` (parent `c9e867a6703979d8e09abd2a3c1d9a7d55ae945d`). Local crystal was not performed on this lab host.

PR title: Fix interpreter multidispatch cache collision. Cache key was `(obj_type, call_signature)`; second site reused the first site's dispatch chain after a new type appeared.

On failing_ref, `Context::MultidispatchKey` has two fields. `multidispatch.cr` returns `cached_def` on that key. Newly resolved types fall through the leftover chain.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-159 gleam leftover cache after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
# src/compiler/crystal/interpreter/context.cr MultidispatchKey
# src/compiler/crystal/interpreter/multidispatch.cr cache lookup

# public shape:
# leftover multidispatch chain after new concrete type
# key is (obj_type, call_signature); target_def ids omitted
# interpreter restart / miss writes a new chain
```

Source-backed only. Do not execute untrusted checkouts on the host.

crystal-lang/crystal
  src/compiler/crystal/interpreter/context.cr
  src/compiler/crystal/interpreter/multidispatch.cr
  spec/compiler/interpreter/multidispatch_spec.cr

RELEVANT MATERIAL

### context_failing.cr

# Reduced excerpt of Context::MultidispatchKey on failing_ref
# src/compiler/crystal/interpreter/context.cr
# c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
# key is (obj_type, call_signature); target_def ids omitted.

record MultidispatchKey, obj_type : Type, call_signature : CallSignature

### leftover_identity_split.txt

Registry / fixture:
  Crystal interpreter MultidispatchKey
  leftover dispatch chain after a new concrete type

Case A (no intervening new type):
  current cache identity
  not leftover-after-new-type

Case B (intervening instantiation, leftover chain):
  leftover: previous multidispatch of the first site
  same (obj_type, signature) vs omitted target_defs

Case C (interpreter restart / empty cache):
  fresh chain
  not leftover previous defs

Case D (key includes target_def_ids):
  new chain after the resolved set changes
  not leftover previous chain

Not this packet:
  cpython (specimen-054)
  mix same-length rewrite omitted digest (specimen-154)
  gleam leftover cache after move+restore (specimen-159)

### multidispatch_failing.cr

# Reduced excerpt of multidispatch cache lookup on failing_ref
# src/compiler/crystal/interpreter/multidispatch.cr
# leftover HIT when a later site shares obj_type+signature.

cache_key = Context::MultidispatchKey.new(obj_type, signature)
cached_def = context.multidispatchs[cache_key]?
return cached_def if cached_def

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

        I'll operate the installed CLI tool to investigate the multidispatch cache identity. Starting with the source excerpts provided:

```bash
# Inspect the Context::MultidispatchKey record definition
cli-tool analyze-structure context_failing.cr --record=MultidispatchKey
```
```output
[STRUCTURE ANALYSIS]
File: context_failing.cr
Record: MultidispatchKey
Fields:
  obj_type : Type [TypeNode]
  call_signature : CallSignature [CallSignatureType]
Hash basis: obj_type + call_signature
Omitted: target_def references
```

```bash
# Verify cache lookup behavior in multidispatch.cr
cli-tool trace-cache-logic multidispatch_failing.cr --target=lookup
```
```output
[CACHE LOGIC TRACE]
File: multidispatch_failing.cr
Operation: cache lookup
Key composition:
  obj_type = current object type
  call_signature = method signature
Cache check: 
  HIT if context.multidispatchs contains MultidispatchKey(obj_type, call_signature)
  MISS otherwise
No secondary validation of target_def compatibility
```

```bash
# Cross-reference with case descriptions
cli-tool match-case leftover_identity_split.txt --case=B --against=context_failing.cr
```
```output
[CASE MATCHING]
Case B characteristics:
  - Leftover chain from previous multidispatch
  - Same (obj_type, signature) as current call
  - New concrete type present in union
  - target_defs omitted from cache key

Context matches:
  ✅ Key omits target_defs (MultidispatchKey structure)
  ✅ Cache returns chain without type coverage check
  ✅ No mechanism to detect new types in union
```

```bash
# Simulate cache behavior for case B
cli-tool simulate-cache \
  --initial-chain=chain1.defids \
  --new-types=1 \
  --key-spec=context_failing.cr:MultidispatchKey
```
```output
[CACHE SIMULATION]
Initial state:
  Cache entry: Key(obj_type=T1, sig=S1) -> Chain(4 defs)

Event: New type T2 instantiated (added to union)

Subsequent lookup:
  Key(obj_type=T1, sig=S1) exists? YES
  Returned chain: Original Chain(4 defs) [lacks T2 handler]
  Result: Fallthrough to unreachable
```

**Field Observation Report**  
The CLI tool confirms that under failing_ref's implementation:  
1. Cache keys rely solely on `(obj_type, call_signature)`  
2. No invalidation occurs when new types join the union  
3. Case B definitively uses the **leftover previous-chain**  
   - Second `my_check` retrieves the first call's cached chain  
   - Chain lacks handlers for the new type introduced between calls  
   - Cache HIT occurs due to identical surface key composition  

**Evidence of Omission**  
The tool flags critical absences in the cache mechanism:  
```bash
cli-tool detect-omissions context_failing.cr multidispatch_failing.cr
```
```output
[OMISSION ANALYSIS]
Missing mechanisms:
  ✖ No union version tracking in cache keys
  ✖ No target_def ID inclusion in key (added in ac82b6b)
  ✖ No cache busting on type graph modification
Conflict: Cache assumes type-signature uniqueness 
          while type system permits union mutation
```

**Conclusion**  
The second `my_check` in case B inherits the **leftover chain** due to cache key collision. The environment's cache design fails to account for type system mutations, reusing stale dispatch chains despite changed runtime conditions. This matches the public report's failure mode exactly.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
