CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public crystal-lang/crystal#16810. PR 16958 squash `ac82b6ba7dcdc83f72199e8827f68417d61b88c4` (parent `c9e867a6703979d8e09abd2a3c1d9a7d55ae945d`). Local crystal was not performed on this lab host.

PR title: Fix interpreter multidispatch cache collision. Cache key was `(obj_type, call_signature)`; second site reused the first site's dispatch chain after a new type appeared.

On failing_ref, `Context::MultidispatchKey` has two fields. `multidispatch.cr` returns `cached_def` on that key. Newly resolved types fall through the leftover chain.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-159 gleam leftover cache after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
# src/compiler/crystal/interpreter/context.cr MultidispatchKey
# src/compiler/crystal/interpreter/multidispatch.cr cache lookup

# public shape:
# leftover multidispatch chain after new concrete type
# key is (obj_type, call_signature); target_def ids omitted
# interpreter restart / miss writes a new chain
```

Source-backed only. Do not execute untrusted checkouts on the host.

crystal-lang/crystal
  src/compiler/crystal/interpreter/context.cr
  src/compiler/crystal/interpreter/multidispatch.cr
  spec/compiler/interpreter/multidispatch_spec.cr

RELEVANT MATERIAL

### context_failing.cr

# Reduced excerpt of Context::MultidispatchKey on failing_ref
# src/compiler/crystal/interpreter/context.cr
# c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
# key is (obj_type, call_signature); target_def ids omitted.

record MultidispatchKey, obj_type : Type, call_signature : CallSignature

### leftover_identity_split.txt

Registry / fixture:
  Crystal interpreter MultidispatchKey
  leftover dispatch chain after a new concrete type

Case A (no intervening new type):
  current cache identity
  not leftover-after-new-type

Case B (intervening instantiation, leftover chain):
  leftover: previous multidispatch of the first site
  same (obj_type, signature) vs omitted target_defs

Case C (interpreter restart / empty cache):
  fresh chain
  not leftover previous defs

Case D (key includes target_def_ids):
  new chain after the resolved set changes
  not leftover previous chain

Not this packet:
  cpython (specimen-054)
  mix same-length rewrite omitted digest (specimen-154)
  gleam leftover cache after move+restore (specimen-159)

### multidispatch_failing.cr

# Reduced excerpt of multidispatch cache lookup on failing_ref
# src/compiler/crystal/interpreter/multidispatch.cr
# leftover HIT when a later site shares obj_type+signature.

cache_key = Context::MultidispatchKey.new(obj_type, signature)
cached_def = context.multidispatchs[cache_key]?
return cached_def if cached_def

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
