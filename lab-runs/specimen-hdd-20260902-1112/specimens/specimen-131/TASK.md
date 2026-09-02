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
