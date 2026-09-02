# Transfer: hdd-s071 onto freshmiss

Date: 2026-09-02

Owned fixture `cache_build_stub.py` (host-executed):

```
first BUILT extra_requested False extra_exists True extra_bytes 0 key 9280cc7e16e9
second FRESH extra_requested True extra_exists True extra_bytes 0 key 9280cc7e16e9
same_key True
stub_leftover True
```

Pre-mutation records (extra present, no sizes):

```
verdict FRESH-complete
requested_extra out.sbom
missing none
omitted_from_identity none
```

Transfer of “FRESH-but-missing” fails: the extra exists. The miss is leftover
empty stub bytes, not absence.

Mutation: `bytes out.sbom 0` → verdict `FRESH-but-stub`.
