# TASK

Crystal's interpreter can keep the identity of a **previous multidispatch chain** after intervening code instantiates a new concrete type that should have been part of the dispatch, because the cache key hashed `(obj_type, call_signature)` and omitted the resolved `target_def` object IDs.

On failing_ref `c9e867a6703979d8e09abd2a3c1d9a7d55ae945d`:

```
record MultidispatchKey, obj_type : Type, call_signature : CallSignature

cache_key = Context::MultidispatchKey.new(obj_type, signature)
cached_def = context.multidispatchs[cache_key]?
return cached_def if cached_def
```

Two call sites that look identical by that key can resolve to different `target_defs` once a new type lands inside the union. The second site reuses the first's leftover chain; the new type matches none of the branches and execution falls through into `raise "unreachable"`.

Public report (crystal-lang/crystal#16810). `v1 = G(M2 | C).new.as(V); v1.my_check` then `v2 = G(C).new.as(V); v2.my_check`. Expected: second call builds a 5-def chain. Actual: leftover 4-def chain, "Reached the unreachable".

In-tree after the repair (not on failing_ref): `target_def_ids` (sorted object IDs) is part of `MultidispatchKey`.

Case A — second call, no intervening new type:
  cache identity is current
  not leftover-after-new-type

Case B — intervening instantiation, leftover chain:
  leftover: previous multidispatch of the first site
  same (obj_type, signature) vs omitted target_defs
  new concrete type present

Case C — interpreter restart / empty multidispatchs:
  fresh chain
  not leftover previous defs

Case D — key includes target_def_ids (post-repair shape, not on failing_ref):
  new chain after the resolved set changes
  not leftover previous chain

The developer wants to know which identity case B actually used for the second `my_check`: leftover previous-chain (target_defs omitted from the key), current resolved set, or omitted (no cache).
