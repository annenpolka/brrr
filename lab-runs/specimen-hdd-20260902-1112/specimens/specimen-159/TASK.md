# TASK

Gleam `PackageLoader` can keep the identity of a **previous compile cache** for module `a` after `a.gleam` was moved out of `src` and later restored, and that cache should not have been current. Removed modules are added to a stale tracker. Cache files stay. Restoring the same-name source with the same bytes takes the leftover previous cache even after dependency `b` changed.

On failing_ref `3767575d05372e4b823c132afacb28e52fbe3aa1`:

```
// Check for any removed modules, by looking at cache files that don't exist in inputs
for cache_file in gleam_cache_files(&self.io, &self.artefact_directory) {
    let module = module_name(&self.artefact_directory, &cache_file);
    if (!inputs.contains_key(&module)) {
        self.stale_modules.add(module);
    }
}
```

`ModuleLoader::load` uses leftover cache when source fingerprint matches:

```
if meta.mtime < source_mtime {
    let source_module = read_source(name.clone())?;
    if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
        return Ok(Input::New(source_module));
    } else if self.mode == Mode::Lsp && self.incomplete_modules.contains(&name) {
        return Ok(Input::New(source_module));
    }
}
Ok(Input::Cached(self.cached(name, meta)))
```

Stale-deps load deletes `cache_meta` only. Removed-module cache files are not deleted. Same-name restored source and leftover cache JOIN.

Public report (gleam-lang/gleam#4320). Add `a.gleam` that calls `b.f`; build; move `a` out; change `b.f`; build; restore `a` unchanged; build. Expected: compile error on the new `b.f`. Actual: leftover previous `a` cache, runtime "function did not exist".

In-tree after the repair (not on failing_ref): cache files are deleted when the source is gone; restoring `a` is a new compile.

Case A — second build, `a.gleam` never left, `b` unchanged:
  cache identity is current
  not leftover-after-move

Case B — `a` moved out then restored, leftover cache:
  leftover: previous compile of `a` (old `b.f`)
  same-name source vs leftover cache files
  `b` already changed

Case C — `gleam clean` / no artefact cache:
  fresh compile of restored `a`
  not leftover previous cache

Case D — cache files deleted on source removal (post-repair shape, not on failing_ref):
  new compile after restore
  not leftover previous `a`

The developer wants to know which identity case B actually used for module `a` after the restore: leftover previous-cache (same-name files stayed), current source vs new `b`, or omitted (no cache).
