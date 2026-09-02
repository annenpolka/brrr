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

# OBSERVED

Public gleam-lang/gleam#4320 (closed 2025-03-20). PR 4325 rebase-merge last commit `b3e1ceb15118c3b4abb0909ef1f2baca6abacd37` (first PR commit on main `588caed189988e96ff51f5e209c4d35151a396cd`, parent `3767575d05372e4b823c132afacb28e52fbe3aa1`). Local gleam was not performed on this lab host.

Issue body: temporarily removed file does not always get recompiled. Cache files of missing sources are not deleted. mtime is not enough when restored content matches the leftover fingerprint. Follow-on of #3873 (mark removed modules stale without deleting cache).

On failing_ref, `PackageLoader::run` adds missing cache modules to `stale_modules`. `ModuleLoader::load` returns `Input::Cached` when fingerprint matches. Restored same-name `a.gleam` JOINs with leftover cache.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-155 clangd leftover BMI.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 3767575d05372e4b823c132afacb28e52fbe3aa1
# compiler-core/src/build/package_loader.rs removed-module loop
# compiler-core/src/build/module_loader.rs fingerprint cache hit

# public shape:
# leftover compile cache of a after a.gleam moved out then restored
# stale tracker add without deleting cache files
# gleam clean / miss writes a new compile
```

Source-backed only. Do not execute untrusted checkouts on the host.

gleam-lang/gleam
  compiler-core/src/build/package_loader.rs
  compiler-core/src/build/module_loader.rs
  compiler-core/src/build/package_loader/tests.rs

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  gleam PackageLoader / ModuleLoader
  leftover compile cache of a after a.gleam moved out then restored

Case A (a never left, b unchanged):
  current cache identity
  not leftover-after-move

Case B (a moved out then restored, leftover cache):
  leftover: previous compile of a (old b.f)
  same-name source vs leftover cache files

Case C (gleam clean / no artefact cache):
  fresh compile of restored a
  not leftover previous cache

Case D (cache files deleted on source removal):
  new compile after restore
  not leftover previous a

Not this packet:
  cpython (specimen-054)
  mix same-length rewrite omitted digest (specimen-154)
  clangd leftover BMI (specimen-155)

### module_loader_failing.rs

// Reduced excerpt of ModuleLoader::load on failing_ref
// compiler-core/src/build/module_loader.rs
// leftover cache HIT when restored source fingerprint matches.

if meta.mtime < source_mtime {
    let source_module = read_source(name.clone())?;
    if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
        return Ok(Input::New(source_module));
    } else if self.mode == Mode::Lsp && self.incomplete_modules.contains(&name) {
        return Ok(Input::New(source_module));
    }
}
Ok(Input::Cached(self.cached(name, meta)))

### package_loader_failing.rs

// Reduced excerpt of PackageLoader::run on failing_ref
// compiler-core/src/build/package_loader.rs
// 3767575d05372e4b823c132afacb28e52fbe3aa1
// removed modules are marked stale; cache files stay.

for cache_file in gleam_cache_files(&self.io, &self.artefact_directory) {
    let module = module_name(&self.artefact_directory, &cache_file);
    if !inputs.contains_key(&module) {
        self.stale_modules.add(module);
    }
}

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
