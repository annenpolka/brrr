KNOWN FIX (sealed): golang/mod CL 815000 merge 57549bfb0d25b5ff7eb4763aa1f029d7e5383232 (CVE-2026-56864 / golang/go#80745).

Lookup cached the full HTTP body (`data`) after authenticating only ParseRecord's `text`. Prefix scan then returned a go.sum line planted in the signed tree-head extension (signed, ignored by ParseTree, never checked against tiles). Repair: cache `text` instead of `data` (`return cached{text, nil}`), so Lookup extracts matching hashes only from the tile-authenticated record. Added TestRejectUnauthenticatedLines: Lookup("golang.org/x/bad", "v1.0.0") against a good-module record plus a bad-module extension line returns err=nil and len(lines)==0. cmd/go checkSumDB then hits sumdbAbsent rather than accepting the planted hash.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
