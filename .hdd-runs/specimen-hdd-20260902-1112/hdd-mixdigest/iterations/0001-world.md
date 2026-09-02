# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public elixir-lang/elixir#11080 (merged 2021-06-28). Squash `350a909eb195ab1c0bc5ad29b7573c36ebd98377` (parent `a677d3c9efb32fe435d8fd102eb8f90272e14da1`). Local elixir/mix was not performed on this lab host.

PR body: hashing content is the right check; tests were added for same-length content change vs identical files with bumped mtime.

On failing_ref, the source record has size not digest. Stale detection is size inequality or Mix.Utils.stale? on mtimes. Same-length rewrite can keep leftover previous modules.

Not this packet: specimen-054 cpython generated-header drift. specimen-086 cargo rustc fingerprint clamped mtime. specimen-147 CDK truncated mtime fingerprint.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref a677d3c9efb32fe435d8fd102eb8f90272e14da1
# lib/mix/lib/mix/compilers/elixir.ex source record / changed

# public shape:
# leftover BEAM after same-length source rewrite
# source record has size not digest
# mix clean / digest in record yields the new modules
```

Source-backed only. Do not execute untrusted checkouts on the host.

elixir-lang/elixir
  lib/mix/lib/mix/compilers/elixir.ex

RELEVANT MATERIAL

### elixir_compile_failing.ex

# Reduced excerpt of Mix.Compilers.Elixir stale check on failing_ref
# lib/mix/lib/mix/compilers/elixir.ex
# a677d3c9efb32fe435d8fd102eb8f90272e14da1
# source record has size not digest.

defrecord :source, source: nil, size: 0, modules: []

changed =
  for source(source: source, size: size, modules: modules) <- all_sources,
      {last_mtime, last_size} = Map.fetch!(sources_stats, source),
      size != last_size or Mix.Utils.stale?([last_mtime | times], [modified]) or
        Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1)),
      do: source
# leftover previous BEAM after same-length rewrite

### leftover_identity_split.txt

Registry / fixture:
  Mix.Compilers.Elixir source record
  leftover BEAM after same-length rewrite

Case A (second compile, same bytes):
  current cache identity
  not leftover-after-rewrite

Case B (same-length rewrite, leftover BEAM):
  leftover: previous modules
  digest omitted; size matches
  future-mtime reset defeats mtime check

Case C (mix clean):
  fresh module identity
  not leftover previous BEAM

Case D (digest on source record):
  new compile after same-length rewrite
  not leftover previous modules

Not this packet:
  cpython generated-header drift (specimen-054)
  cargo rustc fingerprint clamped mtime (specimen-086)

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
