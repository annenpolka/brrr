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
