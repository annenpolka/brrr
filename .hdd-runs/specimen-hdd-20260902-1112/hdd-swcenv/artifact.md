### Field Report: Investigating SWC Cache Key Collision

**Command Sequence 1: Inspect cache key construction**
```sh
$ swc-diag cache-key analyze --file=crates/swc/src/config/mod.rs --function=GlobalInliningPassEnvs::Map
```
```output
Analyzing cache key structure... 
- Key source: `self.vars` only (Vec<(Atom, Atom)>)
- Missing from key: `envs` map (type: Map<Atom, Atom>)
- Key generation: 
    let cache_key = self.vars.iter().map(|(k,v)| (k.clone(),v.clone())).collect::<Vec<_>>()
- Vulnerability: Two compilations with identical vars but different envs will generate identical keys
```

**Observation 1**: The cache key is built exclusively from `self.vars` contents. The `envs` map is used during cache population (`mk_map` call) but omitted from key generation.

---

**Command Sequence 2: Simulate cache collision**
```sh
$ swc-diag cache simulate --scenario=B \
  --env-first='{"REPRO_VALUE":"first"}' \
  --env-second='{"REPRO_VALUE":"second"}' \
  --vars='[]' \
  --cache-type=DashMap
```
```output
[SCENARIO B] Same process, same vars ([]), different envs
┌─────────────┬──────────────────────┬─────────────────────────────┐
│ Compilation │ Cache State          │ process.env.REPRO_VALUE     │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ First       │ MISS (key not found) │ Generated: 'first' (actual) │
│             │ Stored: 'first'      │                             │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ Second      │ HIT (key exists)     │ Retrieved: 'first' (stale)  │
│             │ No update            │ Expected: 'second'          │
└─────────────┴──────────────────────┴─────────────────────────────┘
```

**Observation 2**: When reusing the same process, a cache hit occurs on the second compilation despite changed envs. The actual output (`'first'`) comes from the previous compilation's cached `ValuesMap`.

---

**Command Sequence 3: Verify cache isolation**
```sh
$ swc-diag cache test-isolation --scenario=C \
  --env-first='{"REPRO_VALUE":"first"}' \
  --env-second='{"REPRO_VALUE":"second"}'
```
```output
[SCENARIO C] New process each compilation
┌─────────────┬──────────────────────┬─────────────────────────────┐
│ Compilation │ Cache State          │ process.env.REPRO_VALUE     │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ First       │ MISS (empty cache)   │ Generated: 'first'          │
├─────────────┼──────────────────────┼─────────────────────────────┤
│ Second      │ MISS (empty cache)   │ Generated: 'second'         │
└─────────────┴──────────────────────┴─────────────────────────────┘
```

**Observation 3**: Process isolation prevents cache contamination. Each compilation generates fresh environment values when the cache is empty.

---

**Command Sequence 4: Confirm failure provenance**
```sh
$ swc-diag issue diff --ref=failing_ref --fix_ref=c0b6f12
```
```output
Comparing cache key implementations:
failing_ref (c523551):
  Key: self.vars.clone() only

fixed (c0b6f12):
  Key: self.vars.clone() + self.envs.clone()
  
Critical change: envs map added to cache key
```

**Observation 4**: The fix explicitly adds `envs` to the cache key. This confirms the omission was the root cause of cross-compilation contamination.

---

### Key Findings
1. **Case B Identity Source**: The second compilation outputs `'first'` due to **leftover previous-envs** from the first compilation's cached `ValuesMap`. 
2. **Failure Mechanism**: 
   - Cache hit occurs because identical `vars` (empty) generate identical keys  
   - `envs` map is unused in key generation despite being critical to output
3. **Reproducibility Condition**: 
   - Single process + multiple compilations + changing envs + identical vars → cache collision
4. **Diagnostic Insight**: The minimal verifying question is:  
   *"Does the second compilation's output match the first compilation's envs when vars are identical but explicit envs differ?"*  
   (Answer: Yes, proving cache key incompleteness)

**Conclusion**: The environment value identity in Case B derives solely from the **previous compilation's leftover cache entries**, exposing improper key design. The cache ignores explicit envs configuration when vars match.
