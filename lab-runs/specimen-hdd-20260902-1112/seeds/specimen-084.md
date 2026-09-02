CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# COMMANDS

```
# in-tree on failing_ref 96f62ae6e9cb1b123de383fa2542812c9ba3b7db
# (not executed on this lab host)

# case A (honest, in-tree)
go test golang.org/x/mod/sumdb -run TestClientLookup
# Lookup("rsc.io/sampler", "v1.3.0") ->
#   rsc.io/sampler v1.3.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=

# case C
go test golang.org/x/mod/sumdb -run TestClientGONOSUMDB
# matching GONOSUMDB prefix -> ErrGONOSUMDB

# case D
go test golang.org/x/mod/sumdb -run TestClientFork
# disagreeing signed trees -> ErrSecurity

# case B (fixture, not an in-tree test on this revision)
# log contains only golang.org/x/good@v1.0.0 as a real record
# /lookup/golang.org/x/bad@v1.0.0 = FormatRecord(good) + signed tree
# whose Note.Text is FormatTree + "golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=\n"
# Client.Lookup("golang.org/x/bad", "v1.0.0")
# ParseRecord authenticates the good record; prefix scan walks the cache payload
```

Not executed on this lab host.

golang/mod
  sumdb/client.go
  sumdb/client_test.go
  sumdb/tlog/note.go
  sumdb/note/note.go

RELEVANT MATERIAL

### check_record.go

# Reduced excerpt of checkRecord on failing_ref
# sumdb/client.go
# Authenticates ParseRecord's `text` against tiles. Does not hash the
# signed tree note or its extra lines.

func (c *Client) checkRecord(id int64, data []byte) error {
	c.latestMu.Lock()
	latest := c.latest
	c.latestMu.Unlock()

	if id >= latest.N {
		return fmt.Errorf("cannot validate record %d in tree of size %d", id, latest.N)
	}
	hashes, err := tlog.TileHashReader(latest, &c.tileReader).ReadHashes([]int64{tlog.StoredHashIndex(0, id)})
	if err != nil {
		return err
	}
	if hashes[0] == tlog.RecordHash(data) {
		return nil
	}
	return fmt.Errorf("cannot authenticate record data in server response")
}

### check_sumdb.go

# Reduced excerpt of cmd/go checkSumDB (consumer of Client.Lookup)
# golang/go src/cmd/go/internal/modfetch/fetch.go
# on vendor parent ef97884827ab7f4ec41b0b21c9d40f80092936ab
# lookupSumDB -> sumdb.Client.Lookup lines are the sumdb identity.

	db, lines, err := lookupSumDB(mod)
	if err != nil {
		return module.VersionError(modWithoutSuffix, fmt.Errorf("verifying %s: %v", noun, err))
	}

	have := mod.Path + " " + mod.Version + " " + h
	prefix := mod.Path + " " + mod.Version + " h1:"
	for _, line := range lines {
		if line == have {
			return nil
		}
		if strings.HasPrefix(line, prefix) {
			return module.VersionError(modWithoutSuffix, fmt.Errorf("verifying %s: checksum mismatch\n\tdownloaded: %v\n\t%s: %v"+sumdbMismatch, noun, h, db, line[len(prefix)-len("h1:"):]))
		}
	}
	return module.VersionError(modWithoutSuffix, fmt.Errorf("verifying %s: checksum missing from sumdb response"+sumdbAbsent, noun))

### leftover_lookup_split.txt

Honest log (TestClientLookup fixtures):
  rsc.io/sampler@v1.3.0
    rsc.io/sampler v1.3.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
    rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=

Case A (module is in the log):
  Lookup("rsc.io/sampler", "v1.3.0")
  mustLookup expects the h1 zip line above; err=nil

Case B (module is not in the log; lookup URL names bad):
  authenticated record text:
    golang.org/x/good v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
  signed tree note extension (after FormatTree, before signatures):
    golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
  ParseRecord validates the good record via checkRecord
  ParseTree ignores the extra line
  Lookup prefix "golang.org/x/bad v1.0.0 " is scanned over the cache payload
  (full HTTP body on this revision: record id + text + blank + signed note)

Case C (GONOSUMDB):
  Lookup of a matching prefix -> ErrGONOSUMDB, no lines

Case D (fork):
  Lookup -> ErrSecurity

Case E (cmd/go checkSumDB over Lookup lines):
  exact path vers h -> accept
  other path vers h1: -> sumdbMismatch
  no matching line -> sumdbAbsent

Public #80745:
  coordinating GOPROXY + GOSUMDB can serve module content not in the transparency log
  affect check: rm -r go.sum go.work.sum vendor/ && go mod tidy

### lookup_failing.go

# Reduced excerpt of Client.Lookup on failing_ref
# sumdb/client.go
# After ParseRecord / mergeLatest / checkRecord, the cache payload is `data`
# (full HTTP body). Identity extraction scans that payload for prefix
# path + " " + vers + " ".

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
	}).(cached)
	if result.err != nil {
		return nil, result.err
	}

	prefix := path + " " + vers + " "
	var hashes []string
	for line := range strings.SplitSeq(string(result.data), "\n") {
		if strings.HasPrefix(line, prefix) {
			hashes = append(hashes, line)
		}
	}
	return hashes, nil

### parse_record.go

# Reduced excerpt of record / tree encoding on failing_ref
# sumdb/tlog/note.go
# ParseRecord stops at the first blank line. Remainder is the signed tree note.
# ParseTree ignores extra lines after the three-line tree encoding.

func FormatTree(tree Tree) []byte {
	return fmt.Appendf(nil, "go.sum database tree\n%d\n%s\n", tree.N, tree.Hash)
}

// A future backwards-compatible encoding may add additional lines,
// which the parser can ignore.

func ParseRecord(msg []byte) (id int64, text, rest []byte, err error) {
	i := bytes.IndexByte(msg, '\n')
	id, err = strconv.ParseInt(string(msg[:i]), 10, 64)
	msg = msg[i+1:]
	i = bytes.Index(msg, []byte("\n\n"))
	text, rest = msg[:i+1], msg[i+2:]
	return id, text, rest, nil
}

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
