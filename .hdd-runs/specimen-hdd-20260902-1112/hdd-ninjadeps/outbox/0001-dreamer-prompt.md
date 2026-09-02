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

Ninja's `.ninja_deps` log can keep the identity of a **previous discovered-deps graph** after the producing edge is dirty (sources / command changed). `RecomputeNodeDirty` loads leftover deps before it knows the edge is dirty. The leftover previous edges stay in the graph.

On failing_ref `77d328f5f679bfef14b1f67f3cd431b729bc786f`:

```
if (!edge->deps_loaded_) {
  edge->deps_loaded_ = true;
  // ...
  if (!dep_loader_.LoadDeps(edge, err)) {
    dirty = edge->deps_missing_ = true;
  }
}
```

`LoadDeps` with `deps=` uses `LoadDepsFromLog`: `deps_log_->GetDeps(output)` is accepted if the output mtime is not newer than the stored deps mtime. Dirty/command identity is omitted from that validity check.

Public report (ninja-build/ninja#2666). C++ modules `a`/`b` dyndep flip:

```
# first build: b imports a   (edge a.pcm -> b.pcm)
# edit: a imports b, b does not import a
$ ninja
ninja: error: dependency cycle: CMakeFiles/hasmodules.dir/a.pcm -> CMakeFiles/hasmodules.dir/b.pcm -> CMakeFiles/hasmodules.dir/a.pcm
```

Leftover: previous deps-log edge (`a.pcm -> scanned_Release` / previous import) is loaded while the producing compile is dirty. Combined with the new import, Ninja reports a cycle.

Case A — first build, deps log written for current imports:
  deps identity matches current sources
  not leftover previous graph

Case B — sources flipped, leftover `.ninja_deps` loaded because edge not yet marked dirty:
  leftover: previous discovered-deps identity
  current command/source identity is the flipped import
  cycle reported

Case C — delete `.ninja_deps` then ninja:
  no leftover deps-log identity
  rebuild without previous edges
  not leftover

Case D — output mtime newer than stored deps mtime:
  LoadDepsFromLog rejects stored deps
  not leftover (mtime check fired)

The developer wants to know which identity case B actually used for the module compile graph: leftover previous deps-log edges, current depfile from the flipped sources, or omitted (no discovered deps).

# OBSERVED

Public ninja-build/ninja#2666 (closed 2026-07-19). PR 2680 merge `88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68` (first parent `77d328f5f679bfef14b1f67f3cd431b729bc786f`). Local ninja was not performed on this lab host.

Issue comment (root-cause rewrite): Ninja loads an old deps-log dependency even though the target will be regenerated; leftover obsolete deps cause cycle detection. Ninja should only load a deps file if the target producing it is not dirty.

On failing_ref, `LoadDeps` runs in `RecomputeNodeDirty` before the dirty walk finishes. `LoadDepsFromLog` validity is output mtime vs stored deps mtime. Dirty/command identity is omitted.

Not this packet: specimen-075 rustc incremental fingerprint. specimen-086 cargo rustc extra-filename. Distinct leftover: ninja deps-log identity loaded while the producing edge is dirty.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 77d328f5f679bfef14b1f67f3cd431b729bc786f
# src/graph.cc RecomputeNodeDirty / ImplicitDepLoader::LoadDepsFromLog

# public shape:
# leftover .ninja_deps previous import edges
# ninja: error: dependency cycle: a.pcm -> b.pcm -> a.pcm
```

Source-backed only. Do not execute untrusted checkouts on the host.

ninja-build/ninja
  src/graph.cc
  src/graph.h
  src/deps_log.h
  .ninja_deps

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  .ninja_deps leftover previous import edges
  a.pcm / b.pcm C++ modules
  first build: b imports a
  edit: a imports b

Case A (first build):
  deps log matches current imports
  not leftover

Case B (sources flipped, leftover deps log):
  leftover: previous discovered-deps identity
  LoadDeps before dirty
  cycle a.pcm -> b.pcm -> a.pcm

Case C (delete .ninja_deps then ninja):
  no leftover deps-log identity
  not leftover

Case D (output mtime newer than stored deps):
  LoadDepsFromLog rejects
  not leftover mtime-valid log

Not this packet:
  rustc incremental fingerprint (specimen-075)
  cargo rustc extra-filename (specimen-086)

### load_deps_failing.cc

// Reduced excerpt of RecomputeNodeDirty / LoadDepsFromLog on failing_ref
// src/graph.cc
// 77d328f5f679bfef14b1f67f3cd431b729bc786f
// Leftover deps-log identity is loaded before dirty is known.
// Validity is output mtime vs stored deps mtime. Dirty/command omitted.

  if (!edge->deps_loaded_) {
    edge->deps_loaded_ = true;
    if (!dep_loader_.LoadDeps(edge, err)) {
      dirty = edge->deps_missing_ = true;
    }
  }

bool ImplicitDepLoader::LoadDeps(Edge* edge, string* err) {
  string deps_type = edge->GetBinding("deps");
  if (!deps_type.empty())
    return LoadDepsFromLog(edge, err);
  // ...
}

bool ImplicitDepLoader::LoadDepsFromLog(Edge* edge, string* err) {
  Node* output = edge->outputs_[0];
  DepsLog::Deps* deps = deps_log_ ? deps_log_->GetDeps(output) : NULL;
  if (!deps) return false;
  if (output->mtime() > deps->mtime) return false;  // mtime only
  edge->inputs_.insert(..., nodes, nodes + node_count);
  return true;
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
