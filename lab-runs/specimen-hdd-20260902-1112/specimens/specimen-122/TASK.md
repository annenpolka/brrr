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
