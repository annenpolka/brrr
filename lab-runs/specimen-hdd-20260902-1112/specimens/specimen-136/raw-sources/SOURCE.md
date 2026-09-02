repository: pantsbuild/pants
issue: https://github.com/pantsbuild/pants/issues/16963
pr: https://github.com/pantsbuild/pants/pull/17017
failing_ref (parent of merge on main): 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
fixed_ref (PER_SESSION cache_scope on setuptools_scm VenvPexProcess): 510f1755680d23c3d6c68815ae77ad4a4f836021
merged_at: 2022-09-27T15:33:34Z
pr_author: benjyw
merged_by: benjyw
changed_files: src/python/pants/backend/python/util_rules/vcs_versioning.py
pr_title: Don't cache VCS version outside the current pants session.
scout_note: not 075 rustc incremental. not skipped #23645 env-without-cache-key OPEN. Distinct leftover: git hash omitted from VenvPexProcess identity so leftover setuptools_scm stdout stayed current after amend/commit. job-0585 unique vs 001-135.
