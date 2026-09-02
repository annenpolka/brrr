repository: direnv/direnv
issue: https://github.com/direnv/direnv/pull/1532
pr: https://github.com/direnv/direnv/pull/1532
failing_ref (first parent of merge on master): e261bba8c9f9f32010d046a839ae5de5ae7dda0c
fixed_ref (merge adding NIX_ATTRS_* to values_to_restore): 3580653d9d3a51f093ac96c85505d71b872d7cd0
merged_at: 2026-01-07T20:04:00Z
pr_author: hacker1024
merged_by: zimbatm
changed_files: stdlib.sh
pr_title: fix(use_nix): unset structured attribute variables
scout_note: not 010/149/150/158. leftover NIX_ATTRS paths after use_nix because restore map omitted those names. unique vs 001-159.
