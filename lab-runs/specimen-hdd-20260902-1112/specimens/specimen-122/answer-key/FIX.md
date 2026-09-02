KNOWN FIX (sealed): mesonbuild/meson PR 10728 commit 004575874ffdb77ee997f9c19e0a041d144994d6.

failing_ref is parent 97f248db24fe88495dbe35bbae6eafd643c0c94b.

resolve treated existing meson.build as identity and omitted wrap-file hash, so leftover checkout from the previous wrap file was kept.

PR repair: SHA-256 wrapfile_hash; update_hash_cache writes .meson-subproject-wrap-hash.txt; validate() warns when stored hash differs from current wrap file.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
