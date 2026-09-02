# refpin

Name whether a default ref attached to a pinned rev, and whether that
changed narHash identity.

FIRST is earlier. SECOND is later. The harvest is one verdict, only when
the same rev grew a ref on SECOND and the narHash moved.

```
refpin FIRST SECOND
refpin MISMATCH_LOG
refpin - SECOND
```

`-` is stdin. A flake.lock / nix input JSON object is a lock record
(`url` / `type` ignored). A mismatch log is a pair: pass it as the only
argument.

## Output

| row | meaning |
| --- | --- |
| `verdict` | the join, not three independent flags |
| `ref_present_a` / `ref_present_b` | key presence; `none` is a branch name |
| `ref_attached` | `attached`, `ref_removed`, `both`, `both-disagree`, `none` |
| `identity_changed` | narHash string inequality |

`verdict` is `pinned-rev-default-ref-changed-hash` only for the harvest
AND. Swapping FIRST/SECOND is `ref_removed`, not attach.

Exit 0: `identical`, `lastModified-only`, `metadata-presence`.
Exit 1: harvest hit, harvest miss, rev diverge, parse errors.
Exit 2: usage.

Does not run nix.
