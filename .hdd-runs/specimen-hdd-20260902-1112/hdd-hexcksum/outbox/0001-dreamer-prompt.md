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

# OBSERVED

Public hexpm/hex#821 (closed 2021-01-05). PR 843 squash `90aa44fa8a1e59f2ae65f490edb984e4d6c853d1` (parent `6639c0ad8921fdaf0468d86cc51525c8237e357a`). Local hex was not performed on this lab host.

Issue body: mix hex.update / deps.get CaseClauseError `no case clause matching: {:ok, <<...>>}` at Hex.SCM.fetch after a republished package. Workaround: delete the cached tarball.

On failing_ref, fetch pins `{:ok, ^outer_checksum}` as cached and `{:error, _}` as network fetch. A leftover tarball with a different checksum has no clause.

Not this packet: specimen-074 rubygems frozen lockfile platform identity. specimen-021 poetry leftover.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6639c0ad8921fdaf0468d86cc51525c8237e357a
# lib/hex/scm.ex fetch / cache_path / Hex.Tar.outer_checksum

# public shape:
# leftover ~/.hex/packages/.../pkg-ver.tar after registry checksum change
# fetch matches exact checksum or error only
# rm tarball yields a fresh fetch
```

Source-backed only. Do not execute untrusted checkouts on the host.

hexpm/hex
  lib/hex/scm.ex

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  ~/.hex/packages/<repo>/<package>-<version>.tar
  leftover tarball after registry checksum change

Case A (second deps.get, same checksum):
  current cache identity
  not leftover-after-republish

Case B (checksum changed, leftover cached tarball):
  leftover: previous package-version.tar
  mismatch omitted from fetch path
  CaseClauseError

Case C (rm tarball / cache missing):
  fresh fetch identity
  not leftover previous tarball

Case D (mismatch refetch):
  new tarball after checksum change
  not leftover previous package

Not this packet:
  rubygems frozen lockfile platform identity (specimen-074)

### scm_fetch_failing.ex

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
