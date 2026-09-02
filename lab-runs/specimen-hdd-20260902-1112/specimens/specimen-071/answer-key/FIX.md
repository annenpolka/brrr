# FIX

The stub is written whenever the identity is computed, not when extra is requested.
Presence of `out.sbom` is not production-for-this-request. Identity still omits extra.
Do not treat exists() as extra-complete.
