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
