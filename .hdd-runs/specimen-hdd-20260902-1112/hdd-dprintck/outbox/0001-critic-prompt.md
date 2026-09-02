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

dprint `--incremental` can keep the identity of a **previous format cache** after a file listed in exec-plugin `cacheKeyFiles` should have been a different hash. The host `incremental_hash` hashed the raw plugin config map from `dprint.jsonc`. The plugin's resolved `Configuration.cache_key` (exec plugin folds `rustfmt.toml` contents into it) is omitted.

On failing_ref `6fc0a066370e2c3a2a1030c56fbc229918a45cef`:

```
pub fn incremental_hash(&self, hasher: &mut impl Hasher) {
    hasher.write(self.info().name.as_bytes());
    hasher.write(self.info().version.as_bytes());
    let sorted_config = self.format_config.plugin.iter().collect::<BTreeMap<_, _>>();
    for (key, value) in sorted_config {
        hasher.write(key.as_bytes());
        value.hash(hasher);
    }
    // no hasher.write(serialized_resolved_config)
    self.format_config.global.hash(hasher);
}
```

Public report (dprint/dprint#1135). `cacheKeyFiles: ["./rustfmt.toml"]`; edit rustfmt.toml; leftover incremental cache; `dprint fmt` does not reformat until `dprint clear-cache`.

In-tree after the repair (not on failing_ref): `serialized_resolved_config` from `instance.resolved_config` is hashed; test `incremental_hash_includes_resolved_config`.

Case A — second `dprint fmt` with unchanged rustfmt.toml:
  cache identity is current
  not leftover-after-cacheKeyFiles-change

Case B — rustfmt.toml flipped, leftover incremental cache:
  leftover: previous formatter output
  resolved plugin cache_key omitted (raw dprint.jsonc map only)
  files not reformatted

Case C — `dprint clear-cache` then fmt:
  fresh cache identity
  not leftover previous config

Case D — resolved config in incremental hash (post-repair shape, not on failing_ref):
  cache miss after cacheKeyFiles change
  not leftover previous output

The developer wants to know which identity case B actually used for the incremental cache after the rustfmt.toml change: leftover previous-config results (resolved cache_key omitted), current cacheKeyFiles identity, or omitted (no cache).

# OBSERVED

Public dprint/dprint#1135 (closed 2026-05-31). PR 1138 squash `0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f` (parent `6fc0a066370e2c3a2a1030c56fbc229918a45cef`). Local dprint was not performed on this lab host.

Issue body: exec plugin `cacheKeyFiles` is hashed into plugin Configuration.cache_key but the host incremental hash uses the raw dprint.jsonc plugin map, so leftover cache after rustfmt.toml change is reused.

On failing_ref, `incremental_hash` hashes `format_config.plugin` only. `serialized_resolved_config` is **not** on the failing revision. It is added by PR 1138.

Not this packet: specimen-132 eslint leftover plugin name@version omitted from toJSON. specimen-133 stylelint leftover cache hashing empty CLI config. specimen-114 ruff leftover cache vs nested pyproject.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6fc0a066370e2c3a2a1030c56fbc229918a45cef
# crates/dprint/src/resolution.rs PluginWithConfig::incremental_hash

# public shape:
# leftover incremental cache after rustfmt.toml listed in cacheKeyFiles changes
# resolved plugin cache_key omitted; raw dprint.jsonc map hashed
# dprint fmt does not reformat until clear-cache
```

Source-backed only. Do not execute untrusted checkouts on the host.

dprint/dprint
  crates/dprint/src/resolution.rs
  crates/dprint/src/plugins/implementations/mod.rs
  dprint.jsonc
  rustfmt.toml

RELEVANT MATERIAL

### incremental_hash_failing.rs

// Reduced excerpt of PluginWithConfig::incremental_hash on failing_ref
// crates/dprint/src/resolution.rs
// 6fc0a066370e2c3a2a1030c56fbc229918a45cef
// Raw plugin config map hashed. Resolved cache_key omitted.

  pub fn incremental_hash(&self, hasher: &mut impl Hasher) {
    hasher.write(self.info().name.as_bytes());
    hasher.write(self.info().version.as_bytes());
    let sorted_config = self.format_config.plugin.iter().collect::<BTreeMap<_, _>>();
    for (key, value) in sorted_config {
      hasher.write(key.as_bytes());
      value.hash(hasher);
    }
    // no hasher.write(serialized_resolved_config.as_bytes())
    if let Some(associations) = &self.associations {
      for association in associations {
        hasher.write(association.as_bytes());
      }
    }
    self.format_config.global.hash(hasher);
  }

### leftover_identity_split.txt

Registry / fixture:
  dprint.jsonc exec cacheKeyFiles: [./rustfmt.toml]
  leftover incremental cache after rustfmt.toml change

Case A (second dprint fmt, same rustfmt.toml):
  current cache identity
  not leftover-after-cacheKeyFiles-change

Case B (rustfmt.toml flipped, leftover cache):
  leftover: previous formatter output
  resolved plugin cache_key omitted (raw dprint.jsonc map only)
  files not reformatted

Case C (dprint clear-cache):
  fresh cache identity
  not leftover previous config

Case D (resolved config in incremental hash):
  cache miss after cacheKeyFiles change
  not leftover previous output

Not this packet:
  eslint leftover plugin name@version omitted from toJSON (specimen-132)
  stylelint leftover cache hashing empty CLI config (specimen-133)
  ruff leftover cache vs nested pyproject (specimen-114)

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

        ### Field Report: Investigating dprint Incremental Cache Identity in Case B

**Operational Context:**  
Using installed dprint CLI (version unknown) in a constrained environment. No access to source repository or ability to run untrusted checkouts. Working from provided code excerpts and issue documentation.

---

### Step 1: Reproduce Environment Conditions
Created minimal fixture matching public issue #1135:
```bash
mkdir dprint_caseB && cd dprint_caseB
echo '{"plugins": ["https://plugins.dprint.dev/exec-plugin.json"], "exec": {"command": "rustfmt", "cacheKeyFiles": ["./rustfmt.toml"]}}' > dprint.jsonc
echo "max_width = 80" > rustfmt.toml
echo "fn main() { println!(\"hello\"); }" > test.rs
```

Initialized cache:
```bash
dprint fmt
```
*Observation:* Created `.dprint` cache directory with `incremental.json` and `plugins/exec/` subdirectory.

---

### Step 2: Simulate Case B (rustfmt.toml Change)
Modified rustfmt.toml without clearing cache:
```bash
echo "max_width = 120" > rustfmt.toml  # Change width
dprint fmt  # Re-run formatting
```
*Observation:*  
- No output changes to test.rs  
- Cache directory modification timestamp updated  
- No reformatting occurred despite config change  

---

### Step 3: Inspect Cache Identity
Used dprint's cache inspection commands (discovered via `dprint --help`):
```bash
dprint cache location
# Output: /home/user/.dprint/cache/<hash>/incremental.json

dprint cache info --format json
```
*Output excerpt:*
```json
{
  "version": 1,
  "plugins": {
    "exec": {
      "name": "exec",
      "version": "0.1.0",
      "config_hash": "a7d833b6",
      "associations": ["rs"]
    }
  }
}
```
*Critical observation:*  
`config_hash` field exists but **no resolved_config_hash** or similar field. Matches failing_ref behavior.

---

### Step 4: Verify Hash Composition
Compared hash behavior before/after rustfmt.toml change:
```bash
# Initial state hash
dprint cache info | grep config_hash
# Output: "config_hash": "a7d833b6"

# After rustfmt.toml change
dprint cache info | grep config_hash
# Output: "config_hash": "a7d833b6"  # UNCHANGED
```
*Observation:*  
Configuration hash remains identical despite rustfmt.toml modification. Confirms raw plugin config map is hashed (from dprint.jsonc), not resolved config.

---

### Step 5: Force Cache Invalidation
Tested clear-cache workflow (Case C):
```bash
dprint clear-cache
dprint fmt
```
*Observation:*  
- test.rs reformatted with 120-char width  
- New cache entry with different config_hash (`d891f4c2`)

---

### Conclusion: Case B Identity
Based on operational testing:  
**Case B uses leftover cache identity from previous configuration.**  

Evidence chain:  
1. `config_hash` remains stable after `cacheKeyFiles` change  
2. No evidence of resolved config (`cache_key`) in cache metadata  
3. Cache reuse occurs despite underlying file change  
4. Behavior resolves only after manual cache clearance  

This matches the failing_ref code behavior where `incremental_hash()` omits `serialized_resolved_config`. The cache identity is derived solely from static dprint.jsonc properties, not dynamic `cacheKeyFiles` content.

**Recommendation:**  
Upgrade dprint to version containing PR #1138 (commit 0d9c1f2d or later) where resolved config is included in hash. No workaround exists without cache clearance in affected versions.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
