# nilkeep (clean-room reimpl)

Name a user-null key dropped by empty-map default coalesce and kept by a
null chart default.

This copy compiles records to JSON chart/user values maps, then drives a
two-pass table join: dest nils are copied onto src, then dest nils are
deleted. A null chart value never enters that walk.

```
nilkeep RECORD
nilkeep < RECORD
```

RECORD is a TSV table (`default` / `user` rows) or a JSON document
(`chart` + `user`, or `default` + `user`). TSV compiles under wrap key
`data`. rc=1 when dropped is nonempty.
