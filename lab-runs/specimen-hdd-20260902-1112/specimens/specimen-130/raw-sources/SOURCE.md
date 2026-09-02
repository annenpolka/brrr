repository: Homebrew/brew
issue: https://github.com/Homebrew/brew/issues/23588
pr: https://github.com/Homebrew/brew/pull/23597
failing_ref (merge first parent on main): 4f6e4df964fa22f12591ca4b27e9b52df34b9494
fixed_ref (merge commit): b62af44bc2d4173d113d07648eb78a9facb73fcf
merged_at: 2026-08-21T11:13:54Z
pr_author: MikeMcQuaid
merged_by: MikeMcQuaid
changed_files: Library/Homebrew/test_bot/test_formulae.rb, Library/Homebrew/test/test_bot/test_formulae_spec.rb
pr_title: Invalidate bottle cache for local patches
scout_note: not Homebrew#20936 formula_auditor (job-0539 skip axis). Distinct leftover: bottle cache identity omits local patch files so leftover previous bottle is reused after patch change. Unique vs 001-128 (no Homebrew/brew leftover bottle).
