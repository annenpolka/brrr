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

Ruby `rb_autoload_load` can keep the identity of a **previous autoload / undefined constant** after the autoload helper file was loaded and did not define the constant (the definition moved, or the helper never had it). The const_entry stays `Qundef`. `$LOADED_FEATURES` lists the helper. Deleting the helper from `$LOADED_FEATURES` and accessing the name retries leftover autoload. `Module#constants` still includes the leftover undefined name (Ruby < 3.1).

On failing_ref `ded5a66cb994c5731a17bc9a2420042248a2f1fe`:

```
result = rb_ensure(autoload_require, (VALUE)&state,
   autoload_reset, (VALUE)&state);

if (flag > 0 && (ce = rb_const_lookup(mod, id))) {
    ce->flag |= flag;
}
```

After `autoload_require` of a helper that does not define the constant, there is no `rb_const_remove`. Leftover `Qundef` const_entry stays. Two greps of `ce->value == Qundef` and `const_lookup` cannot replace the JOIN of leftover helper in `$LOADED_FEATURES` vs leftover undefined constant vs retry after delete.

Public report (ruby Bug #15790 / PR 4715). `autoload :X, path` where the file is empty; `X` raises NameError; leftover undefined constant remains; `$LOADED_FEATURES.delete(path)` then `X` autoloads leftover helper again.

In-tree after the repair (not on failing_ref): if the constant is missing or still `Qundef` after require, `rb_const_remove(mod, id)`.

Case A — autoload helper defines the constant:
  current defined identity
  not leftover-after-fail

Case B — helper loaded, constant not defined, leftover Qundef:
  leftover: undefined const_entry / autoload retry after $LOADED_FEATURES delete
  same-name helper vs moved definition
  JOIN of leftover helper file vs leftover undefined name

Case C — no autoload, name never registered:
  missing identity / NameError
  not leftover Qundef

Case D — rb_const_remove after fail (post-repair shape, not on failing_ref):
  constant gone; no leftover autoload retry
  not leftover undefined

The developer wants to know which identity case B actually used for `X` after the helper loaded without defining it: leftover undefined/autoload-retry (same-name helper vs moved definition), current defined constant, or omitted (no const_entry).

# OBSERVED

Public ruby/ruby PR 4715 (merged 2021-10-08). Commit `08759edea8fb75d46c3e75217e6613465426a0d2` (parent `ded5a66cb994c5731a17bc9a2420042248a2f1fe`). Bug #15790. Local ruby was not performed on this lab host.

PR title: Remove autoload for constant if the autoload fails. Test `test_autoload_after_failed_and_removed_from_loaded_features`.

On failing_ref, `rb_autoload_load` does not `rb_const_remove` when the helper does not define the constant. Leftover `Qundef` const_entry. `$LOADED_FEATURES` delete retried leftover autoload. `Module#constants` still had the leftover undefined name (Ruby < 3.1).

Not this packet: specimen-054 cpython generated-code drift. specimen-110 composer leftover abandoned. specimen-157 jest haste leftover mock name. specimen-159 gleam leftover compile cache after move. zeitwerk leftover gem inception (this tick's other packet).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref ded5a66cb994c5731a17bc9a2420042248a2f1fe
# variable.c rb_autoload_load after autoload_require
# leftover Qundef const_entry; $LOADED_FEATURES delete retries autoload

# public shape:
# leftover undefined constant after helper loaded without defining it
# same-name helper vs moved definition JOIN
# Module#constants still includes leftover undefined (Ruby < 3.1)
```

Source-backed only. Do not execute untrusted checkouts on the host.

ruby/ruby
  variable.c
  test/ruby/test_autoload.rb
  spec/ruby/core/module/autoload_spec.rb

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  ruby rb_autoload_load
  leftover undefined constant after helper loaded without defining it

Case A (helper defines the constant):
  current defined identity
  not leftover-after-fail

Case B (helper loaded, constant not defined, leftover Qundef):
  leftover: undefined const_entry / autoload retry after $LOADED_FEATURES delete
  same-name helper vs moved definition

Case C (no autoload, name never registered):
  missing identity / NameError
  not leftover Qundef

Case D (rb_const_remove after fail):
  constant gone; no leftover autoload retry
  not leftover undefined

Not this packet:
  cpython generated-code drift (specimen-054)
  composer leftover abandoned (specimen-110)
  jest haste leftover mock name (specimen-157)
  gleam leftover compile cache after move (specimen-159)
  zeitwerk leftover gem inception (this tick)

### rb_autoload_load_failing.c

/* Reduced excerpt of rb_autoload_load on failing_ref
 * variable.c
 * ded5a66cb994c5731a17bc9a2420042248a2f1fe
 * leftover Qundef const_entry after helper loaded without defining the constant.
 */

result = rb_ensure(autoload_require, (VALUE)&state,
   autoload_reset, (VALUE)&state);

if (flag > 0 && (ce = rb_const_lookup(mod, id))) {
    ce->flag |= flag;
}
/* no rb_const_remove when ce missing or ce->value == Qundef */

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
