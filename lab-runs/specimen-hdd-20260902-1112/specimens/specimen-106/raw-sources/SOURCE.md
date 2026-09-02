repository: pdm-project/pdm
issue: https://github.com/pdm-project/pdm/issues/2852
pr: https://github.com/pdm-project/pdm/pull/2874
failing_ref (merge parent): cc17967ace76ff2fdf455106a6eb26da50685260
fixed_ref (merge commit): 931de2106b37e8dc55efb84de6bf7a704ad28842
merged_at: 2024-05-08T08:18:54Z
merged_by: frostming
pr_author: frostming
changed_files: news/2852.bugfix.md, src/pdm/cli/utils.py, src/pdm/models/setup.py
pr_title: fix: pdm lock --update-reuse expands the $PROJECT_ROOT variable when extra dependencies are included
scout_note: not uv git-vs-directory (006/022/023/102). Distinct leftover: extra path dep URL expanded to absolute file:/// while path stays relative after --update-reuse.
