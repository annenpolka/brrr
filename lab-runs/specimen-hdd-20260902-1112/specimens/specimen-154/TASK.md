# TASK

Mix `Mix.Compilers.Elixir` can keep the identity of a **previous BEAM compile** after a same-length source rewrite and the modules should have been different. The source record stores `size` not a content digest. Stale detection is `size != last_size` or `Mix.Utils.stale?([last_mtime | times], [modified])`. A same-length rewrite whose mtime is reset (future-mtime warning) keeps leftover previous modules.

On failing_ref `a677d3c9efb32fe435d8fd102eb8f90272e14da1`:

```
defrecord :source,
  source: nil,
  size: 0,
  compile_references: [],
  ...

changed =
  for source(source: source, external: external, size: size, modules: modules) <-
        all_sources,
      {last_mtime, last_size} = Map.fetch!(sources_stats, source),
      times = Enum.map(external, &(sources_stats |> Map.fetch!(&1) |> elem(0))),
      size != last_size or Mix.Utils.stale?([last_mtime | times], [modified]) or
        Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1)),
      do: source
```

Source identity is size+mtime, not bytes. Future mtimes are reset to now; then last_mtime is not stale vs the compile timestamp and size still matches.

Public report (elixir-lang/elixir#11080). Same-length rewrite (`A` → `Z`); leftover previous compile. In-tree after the repair: source record has `digest`; same-length content change recompiles; identical files with bumped mtime do not.

Case A — second compile, same bytes, same size:
  cache identity is current
  not leftover-after-rewrite

Case B — same-length rewrite, leftover BEAM:
  leftover: previous modules
  digest omitted; size matches
  future-mtime reset defeats mtime check

Case C — mix clean / forced compile:
  fresh module identity
  not leftover previous BEAM

Case D — digest on the source record (post-repair shape, not on failing_ref):
  new compile after same-length rewrite
  not leftover previous modules

The developer wants to know which identity case B actually used for the compile after the rewrite: leftover previous-BEAM (digest omitted), current source bytes, or omitted (no compile cache).
