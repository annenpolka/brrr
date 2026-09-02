# TASK

`sumdb.Client.Lookup` of a module whose only matching go.sum line sits in the signed tree-head extension of a lookup response does not return the identity the transparency log actually contains for that module.

Honest log (in-tree `TestClientLookup` on golang/mod `96f62ae6e9cb1b123de383fa2542812c9ba3b7db`):

```
rsc.io/sampler@v1.3.0 is a real log record:
rsc.io/sampler v1.3.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
```

Case A — lookup of a module that is in the log:

```
Client.Lookup("rsc.io/sampler", "v1.3.0")
```

On that revision, `mustLookup` expects the tile-authenticated zip hash line above. `err == nil`.

Case B — lookup of a module that is not in the log. The server answers `/lookup/golang.org/x/bad@v1.0.0` with a validly signed payload whose *authenticated record* is a different module, plus an extra go.sum line in the tree-note extension (anything after the tree hash, before the signatures):

Record text (what `tlog.ParseRecord` returns as `text`; `checkRecord` authenticates this against tiles):

```
golang.org/x/good v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
```

Signed tree note text (`tlog.FormatTree` plus one extra line, then `note.Sign`):

```
go.sum database tree
<N>
<tree hash>
golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
```

HTTP body is `FormatRecord(id, goodText)` concatenated with that signed note. `ParseRecord` splits `id`, `text` (good-module lines), `treeMsg` (signed note). `mergeLatest(treeMsg)` verifies the note signature. `tlog.ParseTree` documents that extra lines after the three-line tree encoding are ignored. `checkRecord(id, text)` hashes only `text`.

`Lookup` then walks `result.data` (the cache payload) for lines whose prefix is `path + " " + vers + " "` — here `golang.org/x/bad v1.0.0 `.

Case C — `SetGONOSUMDB` matches the path (`TestClientGONOSUMDB`): `Lookup` returns `ErrGONOSUMDB`, no lines.

Case D — forked trees (`TestClientFork`): `Lookup` returns `ErrSecurity`.

Case E — cmd/go `checkSumDB` (consumer of `lookupSumDB` → `Client.Lookup`) given downloaded hash `h`:
- a returned line equal to `path vers h` → accept
- a returned line with prefix `path vers h1:` that is not `h` → `sumdbMismatch` SECURITY ERROR
- no matching line among Lookup's return → `sumdbAbsent` SECURITY ERROR (`checksum missing from sumdb response`)

The developer wants to know which identity `Client.Lookup("golang.org/x/bad", "v1.0.0")` actually produced in case B: leftover unauthenticated go.sum line (same bytes as the tree-head extension), omitted (empty slice, err=nil), `ErrSecurity`, `cannot authenticate record data`, or the cmd/go `sumdbAbsent` class.
