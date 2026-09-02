# extraedge (clean-room reimpl)

Name a declared extra whose mapped extra-edge did not attach on a reused
package version, and the extra-edge that appears only on the second record.

This copy compiles each record to JSON, then drives a two-pass attach graph:
extras-table edges first, then a walk of declared extras whose neighbors are
all unattached.

```
extraedge FIRST SECOND
```

`-` is stdin (one side only). FIRST/SECOND are TSV maps or JSON documents.

| field | meaning |
| --- | --- |
| `package` / `version` | node identity (once each; extra columns are errors) |
| `declared` | extra names requested (tab-separated; `declared<TAB>` is empty) |
| `extra` | `NAME<TAB>TARGET…` extras table (repeatable) |
| `resolved` | extra-edge targets present on that node (required) |

JSON records use `edges: [{extra, target}]` and `resolved: []` for empty.

Empty lists are `.`. `none` and `-` are ordinary names.

`missed_a` is declared extras whose mapped targets are all absent from
the first resolved list. That is not `declared − resolved` and not
“dump declared if resolved is empty”. `postgresql` attaches when
`psycopg2` is in resolved, because the extras table says so.

Unmapped declared extras are refused (`unmapped`, rc=1). Different
package or version is `identity mismatch` (both identities printed;
harvest columns are `.`; rc=1).

rc=0 only when the identities match and no declared extra missed.
rc=1 on a miss, mismatch, unmapped extra, or parse error.
