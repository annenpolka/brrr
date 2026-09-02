# TASK

bazel-contrib `rules_distroless` apt extension can keep the identity of **previous snapshot facts / packages** after the snapshot URL was upgraded and the package index should have been different. The facts cache key is `dist/component/architecture/Packages` (and Contents). Snapshot URLs are not part of that key. Upgrading the snapshot while leaving dist/component/arch the same still returns leftover previous integrity facts and stale packages.

On failing_ref `42dd9a20c5c761e4131325a2cf594a753ffffa2d`:

```
pkg_fact_key = dist + "/" + component + "/" + architecture + "/Packages"
cnt_fact_key = dist + "/" + component + "/" + architecture + "/Contents"
```

`mctx.facts` then serves `glock.facts().get(pkg_fact_key)` as the integrity for a cache HIT. The URL of the snapshot is not in the key.

Public report (bazel-contrib/rules_distroless#237). Same dist/component/arch; snapshot URL flipped from `.../20251001T023456Z` to `.../20240210T223313Z`; leftover previous facts and stale packages. Rolling suites were already filtered; snapshot suites reused the omitted-URL key.

In-tree after the repair (not on failing_ref): `util.index_fact_key(dist, component, architecture, index_type, urls)` appends a sorted-deduplicated URL token; unused previous-URL facts are pruned.

Case A — second fetch, same snapshot URLs, same dist/component/arch:
  cache identity is current
  not leftover-after-upgrade

Case B — snapshot URL upgraded, leftover facts hit:
  leftover: previous integrity / stale packages
  snapshot URL omitted from fact key
  same dist/component/arch

Case C — facts empty / first fetch / rolling suite not cached:
  fresh index identity
  not leftover previous facts

Case D — snapshot URLs in the fact key (post-repair shape, not on failing_ref):
  new facts after snapshot upgrade
  not leftover previous packages

The developer wants to know which identity case B actually used for the package index after the snapshot URL change: leftover previous-facts packages (URL omitted), current snapshot index, or omitted (no facts cache).
