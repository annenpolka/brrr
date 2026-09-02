CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

SWC `GlobalPassOption::build` can keep the identity of **previous optimizer environment replacements** after a second in-process compile with a different explicit `jsc.transform.optimizer.globals.envs` map, because the process-wide DashMap cache key is built from `self.vars` and omits the configured `envs` map.

On failing_ref `c5235516340959f703c02d91a79ba40df897eb9c`:

```
GlobalInliningPassEnvs::Map(map) => {
    static CACHE: Lazy<DashMap<Vec<(Atom, Atom)>, ValuesMap, FxBuildHasher>> =
        Lazy::new(Default::default);

    let cache_key = self
        .vars
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect::<Vec<_>>();
    if let Some(v) = CACHE.get(&cache_key) {
        (*v).clone()
    } else {
        let map = mk_map(
            cm,
            handler,
            map.iter().map(|(k, v)| (k.clone(), v.clone())),
            false,
        );
        CACHE.insert(cache_key, map.clone());
        map
    }
}
```

Two compilations with the same `vars` (often empty) and different explicit `envs` collide. The later compile reuses leftover replacements from the earlier one. `process.env.REPRO_VALUE` stays `'first'` after the second compile asked for `'second'`.

Public report (swc-project/swc#12166). Follow-up of #12129 (cached-span source-map). Same source compiled twice in one process with different explicit environment values.

In-tree after the repair (not on failing_ref): cache key is the configured `envs` map, sorted so equivalent maps match regardless of iteration order.

Case A — same vars and same envs, second compile:
  cache identity is current
  not leftover-after-env-change

Case B — same vars, different explicit envs, leftover replacements:
  leftover: previous ValuesMap (`'first'`)
  envs map omitted from the key
  process-wide DashMap HIT

Case C — new process / empty CACHE:
  fresh mk_map of current envs
  not leftover previous replacements

Case D — key is the envs map (post-repair shape, not on failing_ref):
  second compile emits `'second'`
  not leftover previous envs

The developer wants to know which identity case B actually used for `process.env.REPRO_VALUE` on the second compile: leftover previous-envs (vars-only key), current envs map, or omitted (no cache).

# OBSERVED

Public swc-project/swc#12166 (merged 2026-09-01). Squash `c0b6f12fe4c3b1d0235a64496560941751e21bd8` (parent `c5235516340959f703c02d91a79ba40df897eb9c`). Local swc was not performed on this lab host.

PR title: fix(swc): key optimizer env cache by configured values. Cache key was built from `globals.vars`. Same vars + different explicit envs collided. Later compile reused leftover environment replacements.

On failing_ref, `GlobalInliningPassEnvs::Map` keys DashMap by `self.vars`. The `map` used to build ValuesMap is omitted from the key.

Not this packet: specimen-156 bun define-table omitted from runtime-transpile hash. specimen-090 webpack persistent cache. specimen-082 bun optional-peer.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c5235516340959f703c02d91a79ba40df897eb9c
# crates/swc/src/config/mod.rs GlobalPassOption::build Map arm

# public shape:
# leftover optimizer env replacements after second compile
# cache key is self.vars; configured envs map omitted
# new process / miss writes current envs
```

Source-backed only. Do not execute untrusted checkouts on the host.

swc-project/swc
  crates/swc/src/config/mod.rs
  crates/swc/tests/simple.rs

RELEVANT MATERIAL

### global_pass_envs_failing.rs

// Reduced excerpt of GlobalPassOption::build Map arm on failing_ref
// crates/swc/src/config/mod.rs
// c5235516340959f703c02d91a79ba40df897eb9c
// cache key is self.vars; configured envs map omitted.

GlobalInliningPassEnvs::Map(map) => {
    static CACHE: Lazy<DashMap<Vec<(Atom, Atom)>, ValuesMap, FxBuildHasher>> =
        Lazy::new(Default::default);

    let cache_key = self
        .vars
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect::<Vec<_>>();
    if let Some(v) = CACHE.get(&cache_key) {
        (*v).clone()
    } else {
        let map = mk_map(
            cm,
            handler,
            map.iter().map(|(k, v)| (k.clone(), v.clone())),
            false,
        );
        CACHE.insert(cache_key, map.clone());
        map
    }
}

### leftover_identity_split.txt

Registry / fixture:
  SWC GlobalPassOption::build envs Map cache
  leftover optimizer env replacements after second compile

Case A (same vars and same envs):
  current cache identity
  not leftover-after-env-change

Case B (same vars, different explicit envs, leftover replacements):
  leftover: previous ValuesMap ('first')
  envs map omitted from the key

Case C (new process / empty CACHE):
  fresh mk_map of current envs
  not leftover previous replacements

Case D (key is the envs map):
  second compile emits 'second'
  not leftover previous envs

Not this packet:
  bun define-table omitted from runtime-transpile hash (specimen-156)
  webpack persistent cache (specimen-090)
  bun optional-peer (specimen-082)

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
