# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public Homebrew/brew#23588 (closed 2026-08-20; PR merged 2026-08-21). PR 23597 merge `b62af44bc2d4173d113d07648eb78a9facb73fcf` (first parent `4f6e4df964fa22f12591ca4b27e9b52df34b9494`). Local brew was not performed on this lab host.

Issue body: test-bot used a bottle from cache even though a local patch file changed without modifying the formula.

On failing_ref, `no_diff?` only passes `formula.path`. `formula.patchlist.grep(LocalPatch)` is **not** part of the cache identity.

Not this packet: Homebrew#20936 formula_auditor revision/compatibility_version (job-0539 skip axis). Distinct leftover: bottle cache identity omits local patch files so leftover previous bottle is reused after patch change.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 4f6e4df964fa22f12591ca4b27e9b52df34b9494
# Library/Homebrew/test_bot/test_formulae.rb no_diff? / artifact_cache_valid?

# public shape:
# leftover artifact-cache/gcc--*.bottle.tar.gz
# formula.rb unchanged; patches/foo.diff changed
# brew install leftover bottle
```

Source-backed only. Do not execute untrusted checkouts on the host.

Homebrew/brew
  Library/Homebrew/test_bot/test_formulae.rb
  Library/Homebrew/test/test_bot/test_formulae_spec.rb
  artifact-cache/<formula>--*.bottle.tar.gz
  <tap>/patches/*.diff

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  artifact-cache leftover bottle
  formula.rb unchanged
  patches/foo.diff old then new
  tap_git_revision of previous bottle

Case A (formula+patch match bottle revision):
  cache valid
  not leftover after patch change

Case B (patch edited, leftover bottle):
  leftover: previous bottle identity
  no_diff? true (formula path only)
  leftover bottle installed

Case C (formula.rb edited):
  no_diff? false
  cache invalid
  not this leftover

Case D (delete artifact-cache bottle):
  fresh bottle
  not leftover cache identity

Not this packet:
  Homebrew#20936 formula_auditor revision (job-0539 skip axis)

### no_diff_failing.rb

# Reduced excerpt of no_diff? / artifact_cache_valid? on failing_ref
# Library/Homebrew/test_bot/test_formulae.rb
# 4f6e4df964fa22f12591ca4b27e9b52df34b9494
# Cache identity is formula path vs tap_git_revision. Local patches omitted.

      def no_diff?(formula, git_ref)
        return false unless repository.directory?
        @fetched_refs ||= T.let([], T.nilable(T::Array[String]))
        if @fetched_refs.exclude?(git_ref)
          test git.to_s, "-C", repository.to_s, "fetch", "origin", git_ref, ignore_failures: true
          @fetched_refs << git_ref if steps.fetch(-1).passed?
        end

        relative_formula_path = formula.path.relative_path_from(repository)
        !!system(git.to_s, "-C", repository.to_s, "diff", "--no-ext-diff", "--quiet", git_ref, "--",
                 relative_formula_path.to_s)
      end

      def artifact_cache_valid?(formula, formulae_dependents: false)
        sha = local_bottle_hash(formula.name, bottle_dir: artifact_cache)
          &.dig(formula.name, "formula", "tap_git_revision")
        return false if sha.blank?
        return false unless no_diff?(formula, sha)
        # ...
      end

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
