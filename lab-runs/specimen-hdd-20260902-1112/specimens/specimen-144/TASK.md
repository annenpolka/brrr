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
