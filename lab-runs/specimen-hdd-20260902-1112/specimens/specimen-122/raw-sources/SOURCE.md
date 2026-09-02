repository: mesonbuild/meson
issue: https://github.com/mesonbuild/meson/issues/10348
pr: https://github.com/mesonbuild/meson/pull/10728
failing_ref (parent of wrap-hash commit on master): 97f248db24fe88495dbe35bbae6eafd643c0c94b
fixed_ref (Warn if wrap file changes): 004575874ffdb77ee997f9c19e0a041d144994d6
merged_at: 2022-09-19T02:48:50Z
pr_author: nosracd
merged_by: eli-schwartz
changed_files: mesonbuild/wrap/wrap.py, mesonbuild/msubprojects.py, unittests/allplatformstests.py
pr_title: Git subproject revision checking
scout_note: not specimen-064/070/092 nix NAR. Distinct leftover: wrap-file identity vs leftover subproject checkout; wrap-hash omitted. meson#10159 closed without PR (CI packagecache discussion). job-0497.
