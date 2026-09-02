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

# OBSERVED

Public bazel-contrib/rules_distroless#237 (merged 2026-07-28). Squash `52a250a1135cd35440a3ff6616fc4f6ebd4819a0` (parent `42dd9a20c5c761e4131325a2cf594a753ffffa2d`). Local rules_distroless was not performed on this lab host.

PR body: the URL of the snapshot was not part of the cache key for facts. Upgrading the snapshot (everything else the same) yielded stale facts and stale packages. Repair bakes snapshot source URLs into the facts key and prunes facts from unused URLs.

On failing_ref, `_fetch_and_parse_sources` builds `pkg_fact_key` from dist/component/architecture only, then `glock.facts().get(pkg_fact_key)` on snapshot suites.

Not this packet: bazel#29298 `env_inherit` action cache local vs remote (SKIP unfixed). specimen-064/070 nix leftover. specimen-136 pants leftover vcs_version.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 42dd9a20c5c761e4131325a2cf594a753ffffa2d
# apt/extensions.bzl pkg_fact_key / mctx.facts

# public shape:
# leftover snapshot facts after snapshot URL upgrade
# fact key is dist/component/arch/Packages; URL omitted
# empty facts / URL in key yields the new index
```

Source-backed only. Do not execute untrusted checkouts on the host.

bazel-contrib/rules_distroless
  apt/extensions.bzl
  apt/private/util.bzl

RELEVANT MATERIAL

### facts_failing.bzl

# Reduced excerpt of apt facts key on failing_ref
# apt/extensions.bzl
# 42dd9a20c5c761e4131325a2cf594a753ffffa2d
# pkg_fact_key is dist/component/arch/Packages. snapshot URL omitted.
# leftover previous integrity after snapshot URL upgrade.

pkg_fact_key = dist + "/" + component + "/" + architecture + "/Packages"
cnt_fact_key = dist + "/" + component + "/" + architecture + "/Contents"
cached_pkg_format = formats.get(pkg_fact_key)
# glock.facts().get(pkg_fact_key) is the leftover integrity on HIT

### leftover_identity_split.txt

Registry / fixture:
  rules_distroless apt mctx.facts
  leftover snapshot facts after URL upgrade

Case A (second fetch, same snapshot URLs):
  current cache identity
  not leftover-after-upgrade

Case B (snapshot URL upgraded, leftover facts hit):
  leftover: previous integrity / stale packages
  snapshot URL omitted from fact key
  same dist/component/arch

Case C (facts empty / rolling suite):
  fresh index identity
  not leftover previous facts

Case D (snapshot URLs in the fact key):
  new facts after snapshot upgrade
  not leftover previous packages

Not this packet:
  bazel#29298 env_inherit local vs remote (SKIP unfixed)
  nix leftover (specimen-064/070)
  pants leftover vcs_version (specimen-136)

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
