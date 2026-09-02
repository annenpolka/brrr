# Reduced excerpt of Hex.SCM.fetch cache on failing_ref
# lib/hex/scm.ex
# 6639c0ad8921fdaf0468d86cc51525c8237e357a
# cache path is package-version.tar. mismatch checksum has no clause.

outer_checksum = Registry.outer_checksum(repo, package, version)
path = cache_path(repo, package, version)

case Hex.Tar.outer_checksum(path) do
  {:ok, ^outer_checksum} ->
    {:ok, :cached}

  {:error, _reason} ->
    # network fetch into path
    {:ok, :new}
end
# leftover {:ok, other_checksum} has no clause
