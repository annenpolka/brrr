# TASK

Homebrew test-bot bottle cache can keep the identity of a **previous bottle** after a local patch file has changed. `no_diff?` diffs only the formula path against the bottle's `tap_git_revision`. Patch files listed on the formula are omitted from that identity.

On failing_ref `4f6e4df964fa22f12591ca4b27e9b52df34b9494`, `artifact_cache_valid?` is:

```
sha = local_bottle_hash(formula.name, bottle_dir: artifact_cache)
        &.dig(formula.name, "formula", "tap_git_revision")
return false if sha.blank?
return false unless no_diff?(formula, sha)
```

and `no_diff?` is:

```
relative_formula_path = formula.path.relative_path_from(repository)
!!system(git, "-C", repository, "diff", "--no-ext-diff", "--quiet", git_ref, "--",
         relative_formula_path.to_s)
```

Public report (Homebrew/brew#23588). CI for homebrew-core gcc:

```
==> brew install artifact-cache/gcc--16.2.0.tahoe.bottle.tar.gz
Notice: Bottle for gcc built at 7df12339119 (Merge e5a39e93eb ... into 860ea91cd8 ...)
```

The formula file itself was unmodified. The local patch the formula refers to changed between runs. Leftover bottle from the previous patch identity was installed.

Case A — first bottle, formula and local patch match `tap_git_revision`:
  cache valid
  not leftover after patch change

Case B — local `patches/foo.diff` edited, formula.rb unchanged, leftover bottle in artifact-cache:
  leftover: previous bottle identity
  current patch identity is the new diff
  `no_diff?` is true (formula path only)
  leftover bottle reused

Case C — formula.rb itself edited:
  `no_diff?` is false
  cache invalid
  not this leftover (formula path is the identity)

Case D — delete artifact-cache bottle then fetch:
  fresh bottle
  not leftover cache identity

The developer wants to know which identity case B actually installed: leftover previous bottle (old patch), current bottle rebuilt for the new patch, or omitted (no bottle).
