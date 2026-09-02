KNOWN FIX (sealed): elixir-lang/elixir PR 11080 squash 350a909eb195ab1c0bc5ad29b7573c36ebd98377.

failing_ref is parent a677d3c9efb32fe435d8fd102eb8f90272e14da1.

Mix.Compilers.Elixir source record stored size not digest. Same-length rewrite could keep leftover previous BEAM when mtime check was defeated.

PR repair: digest on the source record; same-length content change recompiles.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
