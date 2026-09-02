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

Skaffold artifact cache `lookupRemote` can keep the identity of a **previous remote image** after build inputs changed and the digest should have been different. If `RemoteDigest(tag)` succeeds, the failing world returns `found` immediately. It overwrites `artifactCache[hash]` with that digest and does **not** compare the cached digest to the remote one. Reusing the same tag (git sha tag, `:tag1`) after a Dockerfile/dep change still prints `Found Remotely` and skips the rebuild.

On failing_ref `6ea9aeb818b8e371a4386bf044479f86a0a6e885`:

```
func (c *cache) lookupRemote(ctx context.Context, hash, tag string, platforms []specs.Platform) cacheDetails {
	var cacheHit bool
	entry := ImageDetails{}
	if digest, err := docker.RemoteDigest(tag, c.cfg, nil); err == nil {
		log.Entry(ctx).Debugf("Found %s remote", tag)
		entry.Digest = digest
		c.artifactCache[hash] = entry
		return found{hash: hash}
	}
	// ... cacheHit path compares tag@digest only after RemoteDigest(tag) failed ...
	return needsBuilding{hash: hash}
}
```

`hash` is the current input digest. `tag` is the image tag. Remote tag lookup is not the input identity.

Public reports: GoogleContainerTools/skaffold#9248 (lookupRemote always found when the same tag is reused) and #9279 (skaffold build retrieves the same image from cache even when input files change; `Found Remotely` after Dockerfile edit). `--cache-artifacts=false` updates hashes.

In-tree after the repair (not on failing_ref): `found` only when cacheHit **and** remoteDigest == cachedEntry.Digest.

Case A — second build, same inputs, same remote digest:
  cache identity is current
  not leftover-after-input-change

Case B — inputs flipped, same tag, leftover remote lookup:
  leftover: previous image digest under that tag
  digest compare omitted
  `Found Remotely` / no rebuild

Case C — `--cache-artifacts=false`:
  fresh build identity
  not leftover previous digest

Case D — found only if cacheHit and digests equal (post-repair shape, not on failing_ref):
  cache miss / rebuild after input change
  not leftover previous remote image

The developer wants to know which identity case B actually used for the artifact after the input change: leftover previous-tag remote digest (digest compare omitted), current input hash, or omitted (no cache).

# OBSERVED

Public GoogleContainerTools/skaffold#9248 (closed 2024-01-31) and #9279 (closed as the same lookupRemote leftover). PR 9278 squash `9ff4546df8c0d891fde32c24e0d0ef93a8c7404b` (parent `6ea9aeb818b8e371a4386bf044479f86a0a6e885`). Local skaffold was not performed on this lab host.

Issue #9279: bazel/docker artifacts; input files change; `skaffold build` still returns the previous image; `Found Remotely` after Dockerfile `RUN ls`; `--cache-artifacts=false` updates hashes.

On failing_ref, lookupRemote treats a live remote tag as a cache hit for the current input hash without comparing digests.

Not this packet: specimen-097 buildkit leftover git-dir cache key omitting ref. specimen-136 pants leftover process cache vs git hash.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6ea9aeb818b8e371a4386bf044479f86a0a6e885
# pkg/skaffold/build/cache/lookup.go lookupRemote

# public shape:
# leftover Found Remotely after Dockerfile/input change
# RemoteDigest(tag) success returns found; digest compare omitted
# --cache-artifacts=false yields a new hash
```

Source-backed only. Do not execute untrusted checkouts on the host.

GoogleContainerTools/skaffold
  pkg/skaffold/build/cache/lookup.go
  pkg/skaffold/build/cache/cache.go

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  skaffold artifact cache / lookupRemote
  leftover Found Remotely after input change

Case A (second build, same inputs, same digest):
  current cache identity
  not leftover-after-input-change

Case B (Dockerfile/deps flipped, same tag, leftover remote):
  leftover: previous image digest under that tag
  digest compare omitted
  Found Remotely

Case C (--cache-artifacts=false):
  fresh build identity
  not leftover previous digest

Case D (found only if cacheHit and digests equal):
  rebuild after input change
  not leftover previous remote image

Not this packet:
  buildkit leftover git-dir cache key omitting ref (specimen-097)
  pants leftover vcs_version process cache (specimen-136)

### lookup_remote_failing.go

// Reduced excerpt of lookupRemote on failing_ref
// pkg/skaffold/build/cache/lookup.go
// 6ea9aeb818b8e371a4386bf044479f86a0a6e885
// RemoteDigest(tag) success => found. digest compare omitted.

func (c *cache) lookupRemote(ctx context.Context, hash, tag string, platforms []specs.Platform) cacheDetails {
	entry := ImageDetails{}
	if digest, err := docker.RemoteDigest(tag, c.cfg, nil); err == nil {
		log.Entry(ctx).Debugf("Found %s remote", tag)
		entry.Digest = digest
		c.artifactCache[hash] = entry
		return found{hash: hash}
	}
	return needsBuilding{hash: hash}
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

        ### Field Report: Investigating Skaffold Cache Identity in Case B  

**Tool Environment**: Skaffold CLI (v1.47.0, failing_ref `6ea9aeb818b8e371a4386bf044479f86a0a6e885`) with Docker registry emulation.  
**Objective**: Determine which identity (cache key) was used for the artifact after input changes in Case B (Dockerfile/dependency change, same tag, leftover remote digest).  

---

#### Step 1: Initialize Test Fixture  
*Command:*  
```bash 
skaffold build --tag=testcaseb --cache-artifacts=true --verbosity=debug 
```  
*Output (abridged):*  
``` 
Generating tags... 
Tags generated in 2.18ms 
Cache check for artifact [docker-image] - input hash: 7d4a5e3f 
Found [docker-image] remotely with tag testcaseb 
```  
*Observation:*  
- Initial build succeeds. Cache stores `artifactCache[7d4a5e3f] = <old_digest>` (e.g., `sha256:8e6f...`).  

---

#### Step 2: Modify Inputs and Rebuild (Case B)  
*Action:*  
- Edit `Dockerfile` (add `RUN ls`).  
- Rebuild with identical tag `testcaseb`.  

*Command:*  
```bash 
skaffold build --tag=testcaseb --cache-artifacts=true --verbosity=debug 
```  
*Output (abridged):*  
``` 
Generating tags... 
Tags generated in 1.97ms 
Cache check for artifact [docker-image] - input hash: a1b2c3d4 
Found testcaseb remote 
Skipping rebuild: Found remotely 
```  
*Failure/Observation:*  
- New input hash (`a1b2c3d4`) detected (changed due to Dockerfile edit).  
- `lookupRemote` returns `found{hash: a1b2c3d4}` without digest comparison.  
- **Artifact identity**: Cache key `a1b2c3d4` (current input) mapped to *previous remote digest* (from initial build).  

---

#### Step 3: Inspect Cache State  
*Command (using debug dump):*  
```bash 
skaffold debug dump cache --artifact=docker-image 
```  
*Output:*  
``` 
Artifact: docker-image 
Cache Entries: 
  - Hash: 7d4a5e3f -> Digest: sha256:8e6f... (initial build) 
  - Hash: a1b2c3d4 -> Digest: sha256:8e6f... (same as initial) 
```  
*Observation:*  
- Two distinct cache keys (`7d4a5e3f`, `a1b2c3d4`) both reference the *same old digest*.  
- Case B uses **current input hash (`a1b2c3d4`)** as the cache key but inherits the leftover remote digest.  

---

#### Step 4: Verify with Cache Disabled (Case C)  
*Command:*  
```bash 
skaffold build --tag=testcaseb --cache-artifacts=false --verbosity=debug 
```  
*Output:*  
``` 
Cache disabled. Forcing rebuild. 
Building artifact [docker-image]... 
Pushed image: testcaseb@sha256:9a3f... (new digest) 
```  
*Observation:*  
- Fresh build with new digest (`sha256:9a3f...`).  
- Confirms cache was the culprit in Case B.  

---

#### Conclusion: Identity Used in Case B  
- **Cache key**: Current input hash (`a1b2c3d4`).  
- **Digest**: Leftover remote digest from previous build (under reused tag).  
- **Mechanism**: `lookupRemote` overwrote `artifactCache[new_hash]` with the old digest without validation, treating the tag existence as proof of cache hit.  

**Evidence**:  
- Cache dump shows two keys mapping to the same digest.  
- Debug logs confirm `Found remotely` skipped rebuild despite changed inputs.  
- Artifact identity is the *new input hash* corrupted by the *old digest*.  

**Unresolved Uncertainty**:  
- Why did `docker.RemoteDigest()` succeed? (e.g., registry not garbage-collecting old tags).  
- Impact analysis requires registry inspection (outside current scope).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
