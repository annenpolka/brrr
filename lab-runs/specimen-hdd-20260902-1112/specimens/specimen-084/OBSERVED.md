# OBSERVED

Public golang/go issue 80745 / x/mod CL 815000. Failing world in `sumdb/client.go` around parent `96f62ae6e9cb1b123de383fa2542812c9ba3b7db` (golang/mod).

`Client.Lookup` fetches `/lookup/<escaped-path>@<escaped-vers>`, then:

```
id, text, treeMsg, err := tlog.ParseRecord(data)
if err != nil {
    return cached{nil, err}
}
if err := c.mergeLatest(treeMsg); err != nil {
    return cached{nil, err}
}
if err := c.checkRecord(id, text); err != nil {
    return cached{nil, err}
}
if writeCache {
    c.ops.WriteCache(file, data)
}
return cached{data, nil}
```

After that cache fill, it extracts identities from `result.data`:

```
prefix := path + " " + vers + " "
var hashes []string
for line := range strings.SplitSeq(string(result.data), "\n") {
    if strings.HasPrefix(line, prefix) {
        hashes = append(hashes, line)
    }
}
return hashes, nil
```

`tlog.ParseRecord` stops at the first blank line: leading record id, then record text, remainder is the signed tree note. `checkRecord` compares `tlog.RecordHash(text)` to the tile-authenticated hash at `StoredHashIndex(0, id)`. A mismatch is `cannot authenticate record data in server response`.

`tlog.FormatTree` is three newline-terminated lines (`go.sum database tree`, decimal N, base64 Hash). Comment on `ParseTree`: extra text lines after that encoding are ignored (forwards compatibility). `note.Sign` covers the whole `Note.Text`, including those extra lines; they are not themselves log records.

Honest in-tree `TestClientLookup` on that revision: `Lookup("rsc.io/sampler", "v1.3.0")` equals `rsc.io/sampler v1.3.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=`. `TestClientGONOSUMDB` returns `ErrGONOSUMDB` for matching prefixes. `TestClientFork` returns `ErrSecurity` when two signed trees disagree. There is no in-tree case on that revision whose lookup URL names one module while the authenticated record is another and the tree note carries an extra `path vers h1:` line.

cmd/go `checkSumDB` (golang/go `ef97884827ab7f4ec41b0b21c9d40f80092936ab`, the vendor parent of CL 815020) treats Lookup's returned lines as the sumdb identity: exact `path vers h` accepts; a different `h1:` under the same path/version is `sumdbMismatch`; zero matching lines is `sumdbAbsent`.

This packet does not include a local clone; treat the snippets and lookup split as the world. Do not execute untrusted checkouts on the host.
