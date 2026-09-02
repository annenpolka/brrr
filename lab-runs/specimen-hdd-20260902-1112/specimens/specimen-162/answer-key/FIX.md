KNOWN FIX (sealed): direnv/direnv PR 1532 merge 3580653d9d3a51f093ac96c85505d71b872d7cd0.

failing_ref is first parent e261bba8c9f9f32010d046a839ae5de5ae7dda0c.

use_nix values_to_restore omitted NIX_ATTRS_JSON_FILE and NIX_ATTRS_SH_FILE. After the nix shell was gone those leftover paths stayed exported.

PR repair: add those two names to the restore/unset map.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
