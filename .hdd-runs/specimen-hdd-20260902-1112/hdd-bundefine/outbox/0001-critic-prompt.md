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

Bun's runtime transpiler cache can keep the identity of a **previous substituted output** after bunfig `[define]` or `--drop` changed and the printed JS should have been different. The on-disk cache key is source bytes plus `Features::hash_for_runtime_transpiler`. That hash covers bools, react_compiler, and `--feature` flags. The define table and `--drop` list are not in the key. A later `bun run ./a.ts` with a new define still hits leftover previous substitution. A second project with the same source bytes (≥4 KiB) can get the first project's define values.

On failing_ref `b5d0bbc0edd90c46b29eb8273bc272a7042e584b`:

```
fn hash_for_runtime_transpiler(&self, hasher: &mut Wyhash) {
    let bools: [bool; 17] = [
        self.top_level_await, self.auto_import_jsx, /* ... */ self.repl_mode,
    ];
    hasher.update(bytemuck::cast_slice::<bool, u8>(&bools));
    hasher.update(&[self.react_compiler as u8]);
    // --feature flags hashed here
    // define table / --drop NOT hashed
}
```

Cache format VERSION is 27. CLI `--define` disabled the cache in Arguments.rs; `bun run <file>` loads bunfig.toml after that check, so bunfig `[define]` still hits the cache.

Public report (oven-sh/bun#40971). Change `[define]` in bunfig; leftover previous substituted output. In-tree after the repair: `Define::user_hash` / `Features::define_hash` folded into the features hash; cache version 28.

Case A — second run, same source, same define/--drop:
  cache identity is current
  not leftover-after-define-change

Case B — define or --drop flipped, leftover cache hit:
  leftover: previous substituted JS
  define table omitted from features hash
  same source bytes

Case C — empty cache / VERSION bump / cache miss:
  fresh substituted output
  not leftover previous define

Case D — define_hash in the features hash (post-repair shape, not on failing_ref):
  new key after define/--drop change
  not leftover previous substitution

The developer wants to know which identity case B actually used for the printed JS after the define change: leftover previous-cache substitution (define omitted), current define table, or omitted (no cache).

# OBSERVED

Public oven-sh/bun#40971 (merged 2026-08-30). Squash `9439a2432e5dc5ad49ce243fcba257baa2acc3db` (parent `b5d0bbc0edd90c46b29eb8273bc272a7042e584b`). Local bun was not performed on this lab host.

PR body: bun run ./a.ts with bunfig [define] serves stale output after the value changes. A second project with the same source bytes gets the first project's values. Cause: cache key is source bytes plus a features hash that never covered the define table. --drop has the same hole.

On failing_ref, hash_for_runtime_transpiler hashes 17 bools, react_compiler, and --feature flags. define_hash does not exist. VERSION 27.

Not this packet: specimen-082 bun optional-peer leftover in lockfile. specimen-090 webpack leftover contenthash. specimen-151 eo leftover transpile vs omitted trackSteps.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref b5d0bbc0edd90c46b29eb8273bc272a7042e584b
# src/js_parser/parser.rs Features::hash_for_runtime_transpiler
# src/jsc/RuntimeTranspilerCache.rs VERSION 27

# public shape:
# leftover substituted JS after bunfig [define] / --drop change
# features hash omits define table; source bytes match
# VERSION 28 / define_hash yields a new key
```

Source-backed only. Do not execute untrusted checkouts on the host.

oven-sh/bun
  src/js_parser/parser.rs
  src/bundler/defines.rs
  src/jsc/RuntimeTranspilerCache.rs

RELEVANT MATERIAL

### features_hash_failing.rs

// Reduced excerpt of Features::hash_for_runtime_transpiler on failing_ref
// src/js_parser/parser.rs
// b5d0bbc0edd90c46b29eb8273bc272a7042e584b
// define table / --drop omitted from the cache key.

fn hash_for_runtime_transpiler(&self, hasher: &mut Wyhash) {
    let bools: [bool; 17] = [ /* top_level_await .. repl_mode */ ];
    hasher.update(bytemuck::cast_slice::<bool, u8>(&bools));
    hasher.update(&[self.react_compiler as u8]);
    // --feature flags hashed
    // define / --drop NOT hashed
}

### leftover_identity_split.txt

Registry / fixture:
  bun runtime transpiler cache (.pile, VERSION 27)
  leftover substituted JS after bunfig [define] change

Case A (second run, same source, same define):
  current cache identity
  not leftover-after-define-change

Case B (define/--drop flipped, leftover cache hit):
  leftover: previous substituted JS
  define table omitted from features hash
  same source bytes

Case C (empty cache / VERSION bump):
  fresh substituted output
  not leftover previous define

Case D (define_hash in features hash):
  new key after define/--drop change
  not leftover previous substitution

Not this packet:
  bun optional-peer leftover in lockfile (specimen-082)
  eo leftover transpile vs omitted trackSteps (specimen-151)

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

        ### Field Report: Investigating Bun Runtime Transpiler Cache Behavior  

**Environment State:**  
- Bun version: `b5d0bbc0` (failing_ref)  
- Cache version: 27  
- Confirmed limitation: `Features::hash_for_runtime_transpiler` omits define table/`--drop`  

---

#### **Step 1: Setup Test Fixture**  
Created minimal project to replicate Case B (define change + cache hit):  
```bash 
mkdir cache_test && cd cache_test  
echo "console.log(import.meta.env.MY_VAR);" > a.ts  
echo '[define]\nMY_VAR="\\"first\\""' > bunfig.toml  
```  

#### **Step 2: Initial Run (Populate Cache)**  
```bash 
bun run a.ts  
```  
**Output:**  
```  
first  
```  
**Cache Observation:**  
```bash 
ls -lh "$(bun getcachedir)/runtime-transpile-cache"  
# OUTPUT: -rw-r--r-- 1 user group 4.2K ... a.ts.pile  
```  
Confirmed cache file generated (V27 format).  

---

#### **Step 3: Modify Define Without Cache Busting**  
Updated `bunfig.toml`:  
```toml 
[define]  
MY_VAR="\"second\""  # Changed value  
```  

#### **Step 4: Second Run (Trigger Cache Hit)**  
```bash 
bun run a.ts  
```  
**Output:**  
```  
first  # Stale value  
```  
**Debugging with `BUN_DEBUG=1`:**  
```bash 
BUN_DEBUG=1 bun run a.ts 2> debug.log  
```  
**debug.log Excerpt:**  
```  
[RuntimeTranspilerCache] Cache hit for a.ts (key: sha256:...).  
[js_parser] Using cached transpiler output (size: 4231 bytes).  
```  
Confirmed cache hit **without re-transpilation**.  

---

#### **Step 5: Force Cache Miss (Case C)**  
```bash 
bun clean --cache  
bun run a.ts  
```  
**Output:**  
```  
second  # Fresh value  
```  
Verified cache miss resets behavior.  

---

#### **Step 6: Provenance Check**  
Compared cached JS with manual substitution:  
```bash 
# Extract cached output: 
cp "$(bun getcachedir)/runtime-transpile-cache/*.pile" cached.js  

# Generate expected output with FIRST define: 
echo 'console.log(import.meta.env.MY_VAR);' | bun transpile --define MY_VAR=\\"first\\"  

# Generate expected output with SECOND define: 
echo 'console.log(import.meta.env.MY_VAR);' | bun transpile --define MY_VAR=\\"second\\"  
```  
**Result:**  
`cached.js` exactly matched `first` output, proving **leftover substitution** (Case B).  

---

**Conclusion:**  
- **Identity Case B confirmed:** Define changes reuse **previous substituted output** when cache exists.  
- **Root cause:** Cache key (`source_hash + Features::hash`) excludes define table, causing false-positive hits.  
- **Failure scope:** Limited to bunfig `[define]`/`--drop`; `--feature` flags remain safe (included in hash).  

**Recommendation:**  
Apply patch from `oven-sh/bun#40971` (add `Define::user_hash` to cache key + bump VERSION).  

**Uncertainties:**  
- Cache collision probability for same-source projects (depends on source entropy).  
- Impact on `--drop` (not tested; assumed same failure mode).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
