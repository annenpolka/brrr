# FIX (sealed)

django/django PR 19748 / ticket 36560.

Merge commit: ed7c1a56400d64f109f30df3ce697984cdad7c75
Title: Fixed #36560 -- Prevented UpdateCacheMiddleware from caching responses with Cache-Control 'no-cache' or 'no-store'.

UpdateCacheMiddleware already refused `private`. It still stored `no-cache` and `no-store` because those tokens were never consulted.

Repair: treat `private`, `no-cache`, and `no-store` as non-storeable in `process_response`. The existing private test was generalized to loop those three directives with `cache_page` + `cache_control`.

Later follow-ups on the same ticket (CVE-2026-35193 / CVE-2026-8404) changed substring matching to directive-name parsing; those are out of scope for this packet.

Do not expose this file to Dreamers, initial Red Pen, or initial Grounders.
