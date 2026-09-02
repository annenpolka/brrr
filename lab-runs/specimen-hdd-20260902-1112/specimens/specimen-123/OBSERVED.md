# OBSERVED

Public earthly/earthly#3810 merged 2024-02-16. Squash `892a4e03040feca16423d703a2a7ff0a380052cd` (parent `6b297d587cc12bea0372ca333fef34b522388b34`). Local earthly was not performed on this lab host.

PR body: ARGs were not expanded in `--id` of CACHE; example `ARG something` / `CACHE --id $something` resulted in cache id of the literal string `$something`.

On failing_ref, `earthfile2llb/interpreter.go` `handleCache` expands `args[0]` (directory) and `opts.Mode`, then `i.converter.Cache(ctx, dir, opts)` with `opts.ID` untouched. `earthfile2llb/converter.go` `Cache` uses `opts.ID` as `cacheID` when `c.ftrs.GlobalCache && opts.ID != ""`.

Not this packet: specimen-115 (go-task leftover wildcard fingerprint omitting MATCH). Distinct leftover: Earthly CACHE --id identity is the unexpanded ARG token. Not specimen-119 (pixi leftover task-cache filename keyed by env+name omitting args). Not 066/097 docker/buildkit leftover layers.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
