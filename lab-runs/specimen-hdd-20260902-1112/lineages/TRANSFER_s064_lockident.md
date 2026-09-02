# Transfer: hdd-s064 onto lockident

Date: 2026-09-02

lockident names which provided blobs hashed into a 12-char freshness identity.

```
python3 lockident.py --identity e374a4ebd0db \
  --blob rev=e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa \
  --blob ref=master \
  --blob narHash=sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=
```

```
blob         digest12     membership
rev          7e0028208692 omitted
ref          fc613b4dfd67 omitted
narHash      43059f915eb2 omitted
identity  e374a4ebd0db
in_identity  none
omitted  rev,ref,narHash
```

`--identity` is not a git rev and not a narHash. Membership is `sha256(blob)[:12] == identity`.
The s064 join is: same `rev`, `ref` present vs absent, `narHash` diverged.
lockident cannot name that. freshmiss is FRESH-but-missing extra output; worse fit.

Result: TRANSFER FAIL. Harvest is `refpin`.
