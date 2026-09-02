KNOWN FIX (sealed): pypa/pip PR 12392 merge 417ca92b439dba33d707b5da2493358863256bc3.

failing_ref is merge first parent a15dd75d98884c94a77d349b800c7c755d8c34e4.

_make_candidate_from_link mixed base-from-link and extras wrap. A link ireq with extras required only the extras candidate. Constraints looked up a base link with extras=frozenset(), so the explicit path was not reused.

Repair: split _make_base_candidate_from_link (no extras wrap). Link+extras yields the base candidate plus a second extras requirement via install_req_drop_extras. Constraints use the base helper. Tests test_new_resolver_constraint_on_link_with_extra and _indirect.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
