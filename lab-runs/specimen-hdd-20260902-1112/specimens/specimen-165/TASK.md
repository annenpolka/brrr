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
