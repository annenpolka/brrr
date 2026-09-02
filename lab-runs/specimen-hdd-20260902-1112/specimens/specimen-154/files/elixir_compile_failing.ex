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
