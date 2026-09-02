KNOWN FIX (sealed): python/mypy PR 21888 squash 44c0d9f1efc39af78da28fced51261b022252fec.

TypeVar expansion and last-known-value erasure stripped Instance.last_known_value unconditionally, collapsing every PEP 661 sentinel to the shared class. Repair: if last_known_value.is_sentinel_literal(), keep the Instance as-is in expandtype, erasetype, union formatting, and error messages so dict.get(..., Unknown) stays str | Unknown.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
