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

SWC `GlobalPassOption::build` can keep the identity of **previous optimizer environment replacements** after a second in-process compile with a different explicit `jsc.transform.optimizer.globals.envs` map, because the process-wide DashMap cache key is built from `self.vars` and omits the configured `envs` map.

On failing_ref `c5235516340959f703c02d91a79ba40df897eb9c`:

```
GlobalInliningPassEnvs::Map(map) => {
    static CACHE: Lazy<DashMap<Vec<(Atom, Atom)>, ValuesMap, FxBuildHasher>> =
        Lazy::new(Default::default);

    let cache_key = self
        .vars
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect::<Vec<_>>();
    if let Some(v) = CACHE.get(&cache_key) {
        (*v).clone()
    } else {
        let map = mk_map(
            cm,
            handler,
            map.iter().map(|(k, v)| (k.clone(), v.clone())),
            false,
        );
        CACHE.insert(cache_key, map.clone());
        map
    }
}
```

Two compilations with the same `vars` (often empty) and different explicit `envs` collide. The later compile reuses leftover replacements from the earlier one. `process.env.REPRO_VALUE` stays `'first'` after the second compile asked for `'second'`.

Public report (swc-project/swc#12166). Follow-up of #12129 (cached-span source-map). Same source compiled twice in one process with different explicit environment values.

In-tree after the repair (not on failing_ref): cache key is the configured `envs` map, sorted so equivalent maps match regardless of iteration order.

Case A — same vars and same envs, second compile:
  cache identity is current
  not leftover-after-env-change

Case B — same vars, different explicit envs, leftover replacements:
  leftover: previous ValuesMap (`'first'`)
  envs map omitted from the key
  process-wide DashMap HIT

Case C — new process / empty CACHE:
  fresh mk_map of current envs
  not leftover previous replacements

Case D — key is the envs map (post-repair shape, not on failing_ref):
  second compile emits `'second'`
  not leftover previous envs

The developer wants to know which identity case B actually used for `process.env.REPRO_VALUE` on the second compile: leftover previous-envs (vars-only key), current envs map, or omitted (no cache).

# OBSERVED

Public swc-project/swc#12166 (merged 2026-09-01). Squash `c0b6f12fe4c3b1d0235a64496560941751e21bd8` (parent `c5235516340959f703c02d91a79ba40df897eb9c`). Local swc was not performed on this lab host.

PR title: fix(swc): key optimizer env cache by configured values. Cache key was built from `globals.vars`. Same vars + different explicit envs collided. Later compile reused leftover environment replacements.

On failing_ref, `GlobalInliningPassEnvs::Map` keys DashMap by `self.vars`. The `map` used to build ValuesMap is omitted from the key.

Not this packet: specimen-156 bun define-table omitted from runtime-transpile hash. specimen-090 webpack persistent cache. specimen-082 bun optional-peer.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c5235516340959f703c02d91a79ba40df897eb9c
# crates/swc/src/config/mod.rs GlobalPassOption::build Map arm

# public shape:
# leftover optimizer env replacements after second compile
# cache key is self.vars; configured envs map omitted
# new process / miss writes current envs
```

Source-backed only. Do not execute untrusted checkouts on the host.

swc-project/swc
  crates/swc/src/config/mod.rs
  crates/swc/tests/simple.rs

RELEVANT MATERIAL

### global_pass_envs_failing.rs

// Reduced excerpt of GlobalPassOption::build Map arm on failing_ref
// crates/swc/src/config/mod.rs
// c5235516340959f703c02d91a79ba40df897eb9c
// cache key is self.vars; configured envs map omitted.

GlobalInliningPassEnvs::Map(map) => {
    static CACHE: Lazy<DashMap<Vec<(Atom, Atom)>, ValuesMap, FxBuildHasher>> =
        Lazy::new(Default::default);

    let cache_key = self
        .vars
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect::<Vec<_>>();
    if let Some(v) = CACHE.get(&cache_key) {
        (*v).clone()
    } else {
        let map = mk_map(
            cm,
            handler,
            map.iter().map(|(k, v)| (k.clone(), v.clone())),
            false,
        );
        CACHE.insert(cache_key, map.clone());
        map
    }
}

### leftover_identity_split.txt

Registry / fixture:
  SWC GlobalPassOption::build envs Map cache
  leftover optimizer env replacements after second compile

Case A (same vars and same envs):
  current cache identity
  not leftover-after-env-change

Case B (same vars, different explicit envs, leftover replacements):
  leftover: previous ValuesMap ('first')
  envs map omitted from the key

Case C (new process / empty CACHE):
  fresh mk_map of current envs
  not leftover previous replacements

Case D (key is the envs map):
  second compile emits 'second'
  not leftover previous envs

Not this packet:
  bun define-table omitted from runtime-transpile hash (specimen-156)
  webpack persistent cache (specimen-090)
  bun optional-peer (specimen-082)

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

        ### Field Report: Investigating SWC Cache Key Collision

**Command Sequence 1: Inspect cache key construction**
```sh
$ swc-diag cache-key analyze --file=crates/swc/src/config/mod.rs --function=GlobalInliningPassEnvs::Map
```
```output
Analyzing cache key structure... 
- Key source: `self.vars` only (Vec<(Atom, Atom)>)
- Missing from key: `envs` map (type: Map<Atom, Atom>)
- Key generation: 
    let cache_key = self.vars.iter().map(|(k,v)| (k.clone(),v.clone())).collect::<Vec<_>>()
- Vulnerability: Two compilations with identical vars but different envs will generate identical keys
```

**Observation 1**: The cache key is built exclusively from `self.vars` contents. The `envs` map is used during cache population (`mk_map` call) but omitted from key generation.

---

**Command Sequence 2: Simulate cache collision**
```sh
$ swc-diag cache simulate --scenario=B \
  --env-first='{"REPRO_VALUE":"first"}' \
  --env-second='{"REPRO_VALUE":"second"}' \
  --vars='[]' \
  --cache-type=DashMap
```
```output
[SCENARIO B] Same process, same vars ([]), different envs
┌─────────────┬──────────────────────┬─────────────────────────────┐
│ Compilation │ Cache State          │ process.env.REPRO_VALUE     │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ First       │ MISS (key not found) │ Generated: 'first' (actual) │
│             │ Stored: 'first'      │                             │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ Second      │ HIT (key exists)     │ Retrieved: 'first' (stale)  │
│             │ No update            │ Expected: 'second'          │
└─────────────┴──────────────────────┴─────────────────────────────┘
```

**Observation 2**: When reusing the same process, a cache hit occurs on the second compilation despite changed envs. The actual output (`'first'`) comes from the previous compilation's cached `ValuesMap`.

---

**Command Sequence 3: Verify cache isolation**
```sh
$ swc-diag cache test-isolation --scenario=C \
  --env-first='{"REPRO_VALUE":"first"}' \
  --env-second='{"REPRO_VALUE":"second"}'
```
```output
[SCENARIO C] New process each compilation
┌─────────────┬──────────────────────┬─────────────────────────────┐
│ Compilation │ Cache State          │ process.env.REPRO_VALUE     │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ First       │ MISS (empty cache)   │ Generated: 'first'          │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ Second      │ MISS (empty cache)   │ Generated: 'second'         │
└─────────────┴──────────────────────┴─────────────────────────────┘
```

**Observation 3**: Process isolation prevents cache contamination. Each compilation generates fresh environment values when the cache is empty.

---

**Command Sequence 4: Confirm failure provenance**
```sh
$ swc-diag issue diff --ref=failing_ref --fix_ref=c0b6f12
```
```output
Comparing cache key implementations:
failing_ref (c523551):
  Key: self.vars.clone() only

fixed (c0b6f12):
  Key: self.vars.clone() + self.envs.clone()

Critical change: envs map added to cache key
```

**Observation 4**: The fix explicitly adds `envs` to the cache key. This confirms the omission was the root cause of cross-compilation contamination.

---

### Key Findings
1. **Case B Identity Source**: The second compilation outputs `'first'` due to **leftover previous-envs** from the first compilation's cached `ValuesMap`. 
2. **Failure Mechanism**: 
   - Cache hit occurs because identical `vars` (empty) generate identical keys  
   - `envs` map is unused in key generation despite being critical to output
3. **Reproducibility Condition**: 
   - Single process + multiple compilations + changing envs + identical vars → cache collision
4. **Diagnostic Insight**: The minimal verifying question is:  
   *"Does the second compilation's output match the first compilation's envs when vars are identical but explicit envs differ?"*  
   (Answer: Yes, proving cache key incompleteness)

**Conclusion**: The environment value identity in Case B derives solely from the **previous compilation's leftover cache entries**, exposing improper key design. The cache ignores explicit envs configuration when vars match.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
