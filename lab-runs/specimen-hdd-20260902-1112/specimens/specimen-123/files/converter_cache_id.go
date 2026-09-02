// Reduced excerpt of Converter.Cache on failing_ref
// earthfile2llb/converter.go
// 6b297d587cc12bea0372ca333fef34b522388b34
// When GlobalCache and --id are set, cache identity is opts.ID as parsed.

func (c *Converter) Cache(ctx context.Context, mountTarget string, opts commandflag.CacheOpts) error {
	key := cacheKey(c.target)
	cacheID := path.Join("/run/cache", key, path.Clean(mountTarget))
	if c.ftrs.GlobalCache && opts.ID != "" {
		cacheID = opts.ID
	}
	// ...
}
