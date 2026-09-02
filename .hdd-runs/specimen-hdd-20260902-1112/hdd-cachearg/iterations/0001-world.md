# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Earthly's CACHE command can take `--id` so two targets share one cache mount.
On failing_ref `6b297d587cc12bea0372ca333fef34b522388b34`, `handleCache`
expands the CACHE directory and the CACHE mode through `expandArgs`, then
calls `converter.Cache` with `opts.ID` unchanged.

When the converter feature `GlobalCache` is on and `--id` is set,
`converter.Cache` sets:

```
cacheID = opts.ID
```

instead of the default `path.Join("/run/cache", cacheKey(c.target), mountTarget)`.

`opts.ID` is not passed through `expandArgs`. Public report (earthly/earthly#3810):

```
ARG something
CACHE --id $something
```

produces a cache id of the literal string `$something`. Changing the ARG
value does not change the cache identity, so a later ARG value reuses the
leftover mount from the previous ARG value.

Case A — first CACHE --id $something with ARG something=foo:
  cache mount written under identity `$something` (unexpanded token)
  not leftover yet

Case B — later CACHE --id $something with ARG something=bar, leftover foo mount:
  leftover: previous ARG value's cache mount
  expanded ARG omitted from cacheID
  public report: cache id stays the literal `$something`

Case C — CACHE --id with a constant distinct string ("foo" vs "bar"):
  two identities
  not this leftover

Case D — delete the cache mount then CACHE with ARG=bar:
  fresh identity
  not leftover cache id

The directory path of CACHE *is* expanded. Mode is expanded. Only `--id`
is omitted.

The developer wants to know, for case B, which cache-mount identity Earthly
actually used: leftover unexpanded `$something` from foo, an expanded
`bar` id, or omitted (no --id, target-keyed default).

# OBSERVED

Public earthly/earthly#3810 merged 2024-02-16. Squash `892a4e03040feca16423d703a2a7ff0a380052cd` (parent `6b297d587cc12bea0372ca333fef34b522388b34`). Local earthly was not performed on this lab host.

PR body: ARGs were not expanded in `--id` of CACHE; example `ARG something` / `CACHE --id $something` resulted in cache id of the literal string `$something`.

On failing_ref, `earthfile2llb/interpreter.go` `handleCache` expands `args[0]` (directory) and `opts.Mode`, then `i.converter.Cache(ctx, dir, opts)` with `opts.ID` untouched. `earthfile2llb/converter.go` `Cache` uses `opts.ID` as `cacheID` when `c.ftrs.GlobalCache && opts.ID != ""`.

Not this packet: specimen-115 (go-task leftover wildcard fingerprint omitting MATCH). Distinct leftover: Earthly CACHE --id identity is the unexpanded ARG token. Not specimen-119 (pixi leftover task-cache filename keyed by env+name omitting args). Not 066/097 docker/buildkit leftover layers.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6b297d587cc12bea0372ca333fef34b522388b34
# earthfile2llb/interpreter.go handleCache
# earthfile2llb/converter.go Cache

# public shape:
# ARG something
# CACHE --id $something /id-test
# leftover cache mount identity is the unexpanded token
# later ARG something=bar reuses leftover foo mount
```

Source-backed only. Do not execute untrusted checkouts on the host.

earthly/earthly
  earthfile2llb/interpreter.go
  earthfile2llb/converter.go
  tests/cache-cmd.earth
  tests/Earthfile

RELEVANT MATERIAL

### converter_cache_id.go

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

### handle_cache_failing.go

// Reduced excerpt of Interpreter.handleCache on failing_ref
// earthfile2llb/interpreter.go
// 6b297d587cc12bea0372ca333fef34b522388b34
// Directory and mode are expanded. opts.ID is not.

func (i *Interpreter) handleCache(ctx context.Context, cmd spec.Command) error {
	opts := commandflag.CacheOpts{}
	args, err := flagutil.ParseArgsCleaned("CACHE", &opts, flagutil.GetArgsCopy(cmd))
	dir, err := i.expandArgs(ctx, args[0], false, false)
	expandedMode, err := i.expandArgs(ctx, opts.Mode, false, false)
	opts.Mode = expandedMode
	if !path.IsAbs(dir) {
		dir = path.Clean(path.Join("/", i.converter.mts.Final.MainImage.Config.WorkingDir, dir))
	}
	if err := i.converter.Cache(ctx, dir, opts); err != nil {
		return i.wrapError(err, cmd.SourceLocation, "apply CACHE")
	}
	return nil
}

### leftover_identity_split.txt

Registry / fixture:
  ARG something
  CACHE --id $something /id-test
  leftover cache mount identity = literal $something

Case A (first CACHE, ARG something=foo):
  writes cache under unexpanded token
  not leftover yet

Case B (later CACHE, ARG something=bar, leftover foo mount):
  leftover: foo cache under $something
  expanded ARG omitted from cacheID

Case C (CACHE --id foo vs CACHE --id bar constants):
  two identities
  not this leftover

Case D (delete cache mount then ARG=bar):
  fresh identity
  not leftover

Not this packet:
  go-task leftover wildcard fingerprint omitting MATCH (specimen-115)
  pixi leftover task-cache filename env+name omitting args (specimen-119)
  docker/buildkit leftover layers (066/097)

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
