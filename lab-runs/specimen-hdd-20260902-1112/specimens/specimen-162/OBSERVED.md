# OBSERVED

Public direnv/direnv#1532 (merged 2026-01-07). Merge `3580653d9d3a51f093ac96c85505d71b872d7cd0` (first parent `e261bba8c9f9f32010d046a839ae5de5ae7dda0c`). Local direnv was not performed on this lab host.

PR title: fix(use_nix): unset structured attribute variables. `NIX_ATTRS_JSON_FILE` / `NIX_ATTRS_SH_FILE` point at files that do not exist after the Nix shell is destroyed. stdenv setup crashes on nested non-pure shells.

On failing_ref, `use_nix` restore map has NIX_BUILD_TOP and TMP* and terminfo. Structured-attrs names are omitted. direnv dump keeps leftover exported paths.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-149 compose listed-without-equals. specimen-150 systemd `::` cwd. specimen-158 vcpkg Windows sz==0 JOIN.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
