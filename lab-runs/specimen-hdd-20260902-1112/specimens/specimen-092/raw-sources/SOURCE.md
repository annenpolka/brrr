repository: NixOS/nix
issue: https://github.com/NixOS/nix/issues/15198
pr: https://github.com/NixOS/nix/pull/15199
failing_ref (PR base on NixOS/nix): d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
fixed_ref (PR head on manveru/nix, not merged as of scout): 5ad2cd9a3051f812801a537e485aff160333da35
head_sha: 5ad2cd9a3051f812801a537e485aff160333da35
created_at: 2026-02-11T13:13:24Z
author: manveru
changed_files: src/libfetchers/fetchers.cc, tests/functional/flakes/cache-poisoning.sh, tests/functional/flakes/meson.build
pr_title: fix: use narHash as fetchToStore cache key in substitution fast path
scout_note: not specimen-064 / NixOS/nix#16391 (detached HEAD getDefaultRef master fallback; same rev, added ref field, different hashed tree). not Honor-KILL lockident (caller --identity vs sha256(bytes)[:12] of named blobs). Distinct split: flake.lock rev fingerprint is the fetchToStore cache key; flake.lock narHash is the store-path identity; after rev-only lock edit the cache maps new rev to old NAR path.
related-not-this: #6061 path-input hash after GC (same cache family, different trigger); #6759 registry pin; #10153 git-lfs pointer vs smudge NAR; #10588 nested submodules; #11428 CRLF git export NAR across nix 2.19/2.20.
