# TASK

Hex `Hex.SCM.fetch` can keep the identity of a **previous cached tarball** after the registry checksum changed (`mix hex.publish --replace`) and `mix deps.get` should have fetched a different package. The cache path is `~/.hex/packages/<repo>/<package>-<version>.tar`. Fetch only matches exact `outer_checksum` or `{:error, _}`. A cached tarball whose checksum differs from the registry is leftover previous package-version identity (CaseClauseError; workaround `rm` the tarball).

On failing_ref `6639c0ad8921fdaf0468d86cc51525c8237e357a`:

```
outer_checksum = Registry.outer_checksum(repo, package, version)
path = cache_path(repo, package, version)

case Hex.Tar.outer_checksum(path) do
  {:ok, ^outer_checksum} ->
    {:ok, :cached}

  {:error, _reason} ->
    case Hex.Repo.get_tarball(repo, package, version) do
      {:ok, {200, body, _headers}} ->
        File.mkdir_p!(Path.dirname(path))
        File.write!(path, body)
        {:ok, :new}
      ...
    end
end
```

`{:ok, other_outer_checksum}` is not a clause. Cache identity is package+version path, not registry checksum.

Public report (hexpm/hex#821). Publish; deps.get caches tarball; republish `--replace` so checksum changes; second deps.get CaseClauseError on leftover cached bytes. `rm ~/.hex/packages/<repo>/<package>-<version>.tar` yields a fresh fetch.

In-tree after the repair (not on failing_ref): mismatch warns and `do_fetch`s.

Case A — second deps.get, same registry checksum:
  cache identity is current
  not leftover-after-republish

Case B — registry checksum changed, leftover cached tarball:
  leftover: previous package-version.tar bytes
  checksum mismatch omitted from fetch path
  CaseClauseError / leftover package

Case C — cache file missing / rm tarball:
  fresh fetch identity
  not leftover previous tarball

Case D — mismatch refetch (post-repair shape, not on failing_ref):
  new tarball after checksum change
  not leftover previous package

The developer wants to know which identity case B actually used for the package after the checksum change: leftover previous-cache tarball (mismatch omitted), current registry tarball, or omitted (no cache).
