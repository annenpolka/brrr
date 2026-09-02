# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
