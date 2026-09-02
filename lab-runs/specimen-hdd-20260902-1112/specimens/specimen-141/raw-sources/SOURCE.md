repository: spack/spack
issue: https://github.com/spack/spack/issues/51553
pr: https://github.com/spack/spack/pull/51931
failing_ref (parent of merge on develop): 194e0da658190ae0219bd9576bd7ce1099ce1e0b
fixed_ref (cache after solve, re-finalize on hit): 525775aa9b3e9500f661508456902c7634c23655
merged_at: 2026-05-29T07:23:46Z
pr_author: tgamblin
merged_by: tgamblin
changed_files: lib/spack/spack/solver/asp.py, lib/spack/spack/spec.py, tests, concretizer.yaml
pr_title: solver: cache concretization results immediately after solve
scout_note: not 136 pants process cache. not 140 rush operation graph. Distinct leftover: fully-finalized spec hashes stored so leftover dag_hash after package.py change stayed current. unique vs 001-140.
