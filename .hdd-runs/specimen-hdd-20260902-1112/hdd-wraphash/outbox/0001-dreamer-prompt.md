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

Meson wrap resolution can keep the identity of a **previous wrap-file checkout** after the wrap file on disk has a new revision / source_hash / directory. If `subprojects/<dir>/meson.build` already exists, `Resolver.resolve` returns that leftover directory and does not compare wrap-file identity.

On failing_ref `97f248db24fe88495dbe35bbae6eafd643c0c94b`, `PackageDefinition` has no `wrapfile_hash`. There is no `.meson-subproject-wrap-hash.txt`. `resolve` is:

```
# The directory is there and has meson.build? Great, use it.
if method == 'meson' and os.path.exists(meson_file):
    return rel_path
```

Wrap-file contents (revision, source_url, source_hash, directory) are not that identity. Leftover checkout from the previous wrap file is kept.

Public report (mesonbuild/meson#10348): change wrap-file version/revision; ninja does not reconfigure; leftover subproject stays. meson#10159 (CI packagecache leftover across wrap-file updates) closed without a PR.

In-tree after the repair (not on failing_ref): `wrapfile_hash` SHA-256 of the wrap file; `update_hash_cache` writes `.meson-subproject-wrap-hash.txt`; `validate()` warns when stored hash ≠ current wrap-file hash. Unit test `test_wrap_git` changes `revision = master` to `not-master` and expects `revision may be out of date` on `--reconfigure`.

Case A — first `meson setup`, wrap matches the checkout just fetched:
  no leftover
  wrap-hash omitted (file does not exist yet)

Case B — wrap file edited (new revision / source_hash), leftover `subprojects/<dir>/meson.build`:
  leftover: previous wrap-file checkout
  current wrap-file identity is the new revision
  resolve returns leftover directory
  no wrap-hash compare

Case C — delete `subprojects/<dir>` then setup:
  fresh fetch from current wrap file
  not leftover checkout

Case D — cmake method with leftover directory (`CMakeLists.txt` present):
  leftover cmake checkout used
  same omitted wrap-file identity (meson path is the reported one)

The developer wants to know which identity case B actually used for the subproject: leftover previous wrap-file checkout, current wrap-file identity, or omitted (no subproject directory).

# OBSERVED

Public mesonbuild/meson#10348 (closed 2022-09-19). PR 10728 commit `004575874ffdb77ee997f9c19e0a041d144994d6` (parent `97f248db24fe88495dbe35bbae6eafd643c0c94b`). meson#10159 closed without a pull request. Local meson was not performed on this lab host.

Issue body: changing wrap-file contents does not trigger rebuild/reconfigure of the subproject.

On failing_ref, `resolve` treats an existing `meson.build` as identity. Wrap-file hash is not computed. `.meson-subproject-wrap-hash.txt` is not written. `update_hash_cache` / `validate` are **not** on the failing revision. They are added by PR 10728.

Not this packet: specimen-064/070/092 (nix NAR hash leftover vs rev). Distinct leftover: wrap-file identity vs leftover subproject checkout with wrap-hash omitted.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 97f248db24fe88495dbe35bbae6eafd643c0c94b
# mesonbuild/wrap/wrap.py Resolver.resolve

# public shape:
# leftover subprojects/<dir>/meson.build from previous wrap
# wrap file now has a different revision
# meson setup / ninja does not pick up wrap-file identity
```

Source-backed only. Do not execute untrusted checkouts on the host.

mesonbuild/meson
  mesonbuild/wrap/wrap.py
  mesonbuild/msubprojects.py
  unittests/allplatformstests.py
  subprojects/<dir>/.meson-subproject-wrap-hash.txt

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  subprojects/wrap_git.wrap revision = master then not-master
  leftover subprojects/<dir>/meson.build
  no .meson-subproject-wrap-hash.txt on failing_ref

Case A (first meson setup):
  checkout matches wrap
  wrap-hash omitted (no file)

Case B (wrap file edited, leftover meson.build):
  leftover: previous wrap-file checkout
  current wrap-file identity is new revision
  resolve returns leftover directory

Case C (delete subprojects/<dir> then setup):
  fresh fetch
  not leftover checkout

Case D (cmake leftover CMakeLists.txt):
  leftover cmake checkout
  wrap-file identity still omitted

Not this packet:
  nix NAR leftover vs rev (specimen-064/070/092)
  meson#10159 CI packagecache discussion (no PR)

### wrap_resolve_failing.py

# Reduced excerpt of Resolver.resolve on failing_ref
# mesonbuild/wrap/wrap.py
# 97f248db24fe88495dbe35bbae6eafd643c0c94b
# Existing meson.build is the identity. Wrap-file hash is omitted.

        meson_file = os.path.join(self.dirname, 'meson.build')
        cmake_file = os.path.join(self.dirname, 'CMakeLists.txt')

        # The directory is there and has meson.build? Great, use it.
        if method == 'meson' and os.path.exists(meson_file):
            return rel_path
        if method == 'cmake' and os.path.exists(cmake_file):
            return rel_path

# PackageDefinition.__init__ has no wrapfile_hash.
# get_hashfile / update_hash_cache / validate do not exist.

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
