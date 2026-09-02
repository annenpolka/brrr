repository: golang/mod
cl: https://go-review.googlesource.com/c/mod/+/815000
issue: https://github.com/golang/go/issues/80745
cve: CVE-2026-56864
go_vuln: GO-2026-6180
failing_ref (CL parent): 96f62ae6e9cb1b123de383fa2542812c9ba3b7db
fixed_ref (merged CL 815000): 57549bfb0d25b5ff7eb4763aa1f029d7e5383232
parent_subject: sumdb/tlog: fix TileHashReader authentication bypass
fixed_subject: sumdb: ignore unrelated hashes in Lookup
merged_at: 2026-08-13T19:00:00Z
merged_by: Neal Patel
author: Roland Shoemaker
changed_files: sumdb/client.go, sumdb/client_test.go
vendor_into_go_cl: https://go-review.googlesource.com/c/go/+/815020
vendor_failing_parent: ef97884827ab7f4ec41b0b21c9d40f80092936ab
vendor_fixed_ref: 1522b2d8c820f339ba47a2b40eee3a6fb9d713be
scout_note: assigned specimen-083; that id already held DERIVED_VERIFIED local-fixture (go.sum zip vs go.mod-only, golang/go#41341). Not rust-lang/rust#133828 (specimen-075). golang/mod absent from SPECIMEN_INDEX. Distinct leftover: Lookup go.sum identity taken from a signed tree-head extension that was never a log record. Independently re-pinned from Gerrit CL 815000 (current_revision 57549bfb, parent 96f62ae6) and CL 815020 (current_revision 1522b2d8, parent ef978848).
