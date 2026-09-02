# OBSERVED

Public mesonbuild/meson#10348 (closed 2022-09-19). PR 10728 commit `004575874ffdb77ee997f9c19e0a041d144994d6` (parent `97f248db24fe88495dbe35bbae6eafd643c0c94b`). meson#10159 closed without a pull request. Local meson was not performed on this lab host.

Issue body: changing wrap-file contents does not trigger rebuild/reconfigure of the subproject.

On failing_ref, `resolve` treats an existing `meson.build` as identity. Wrap-file hash is not computed. `.meson-subproject-wrap-hash.txt` is not written. `update_hash_cache` / `validate` are **not** on the failing revision. They are added by PR 10728.

Not this packet: specimen-064/070/092 (nix NAR hash leftover vs rev). Distinct leftover: wrap-file identity vs leftover subproject checkout with wrap-hash omitted.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
