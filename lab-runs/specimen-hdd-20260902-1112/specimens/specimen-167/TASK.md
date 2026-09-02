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
