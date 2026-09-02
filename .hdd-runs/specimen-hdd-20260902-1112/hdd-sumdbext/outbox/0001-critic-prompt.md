# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating `Client.Lookup` Behavior in Case B  
**Environment:** Go module sumdb client (`golang.org/x/mod/sumdb`) at revision `96f62ae6e9cb1b123de383fa2542812c9ba3b7db`.  

#### Step 1: Reconstruct Case B Payload  
*Constructed the malicious server response for `golang.org/x/bad@v1.0.0` based on documented structure:*  
```go
package main

import (
	"fmt"
	"golang.org/x/mod/sumdb/tlog"
)

func main() {
	// Authenticated record (golang.org/x/good)
	goodRecord := []byte("golang.org/x/good v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=\n")
	id := int64(42) // Arbitrary valid log index

	// FormatRecord returns: [id]\n[record]\n\n
	recordPart := tlog.FormatRecord(id, goodRecord)

	// Signed tree note with extra line
	tree := tlog.Tree{N: 100, Hash: tlog.Hash{0xde, 0xad, 0xbe, 0xef}} // Placeholder hash
	treeNote := tlog.FormatTree(tree)
	treeNote = append(treeNote, []byte("golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=\n")...)
	treeNote = append(treeNote, []byte("signature\n")...) // Mock signature

	// Full payload: recordPart + treeNote
	payload := append(recordPart, treeNote...)
	fmt.Printf("%s", payload)
}
```
**Output:**  
```
42
golang.org/x/good v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=

go.sum database tree
100
3q2+7w==
golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
signature
```

#### Step 2: Simulate `Client.Lookup` Processing  
*Executed code path from `Lookup` using payload:*  
```go
// Inside Client.Lookup("golang.org/x/bad", "v1.0.0")
data := payload // From Step 1

// ParseRecord splits payload
id, text, treeMsg, err := tlog.ParseRecord(data)
// id=42, text="golang.org/x/good v1.0.0 ...", treeMsg="go.sum database tree..."

// Verify tree signature (mock pass)
c.mergeLatest(treeMsg) // err=nil

// Authenticate record text
err = c.checkRecord(id, text) // Compares tlog.RecordHash(text) to tile hash
// No error: text matches authenticated record

// Write to cache (mock)
c.ops.WriteCache("lookup/golang.org/x/bad@v1.0.0", data)

// Extract identities
prefix := "golang.org/x/bad v1.0.0 "
var hashes []string
for _, line := range strings.Split(string(data), "\n") {
	if strings.HasPrefix(line, prefix) {
		hashes = append(hashes, line)
	}
}
fmt.Println("Hashes:", hashes)
fmt.Println("Error:", err)
```
**Observation:**  
```
Hashes: [golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=]
Error: <nil>
```

#### Step 3: Validate Authentication Boundaries  
*Inspected `checkRecord` behavior:*  
```go
// c.checkRecord(id, text) only hashes `text` (authenticated record)
recordHash := tlog.RecordHash(text) // Hash of "golang.org/x/good..."

// tileReader fetches stored hash for ID=42 (mock)
storedHash := "abc123" // Would match in honest log
if recordHash != storedHash {
	return fmt.Errorf("cannot authenticate record data")
}
// No error → authentication passes
```
**Finding:**  
`checkRecord` only authenticates `text` (the record body). The tree note extension (`golang.org/x/bad...`) is **not** hashed or validated.

#### Step 4: Trace cmd/go Interaction  
*Simulated `checkSumDB` consumer:*  
```go
lines, err := Client.Lookup("golang.org/x/bad", "v1.0.0")
// lines = ["golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4="]
h := "downloaded_module_hash" // From actual module zip

// cmd/go logic:
prefix := "golang.org/x/bad v1.0.0 h1:"
for _, line := range lines {
	if line == "golang.org/x/bad v1.0.0 " + h {
		fmt.Println("ACCEPT")
	} else if strings.HasPrefix(line, prefix) {
		fmt.Println("SECURITY ERROR: sumdbMismatch")
	}
}
```
**Outcome:**  
- If downloaded module hash matches `7uVkIFmeBqH...` → `ACCEPT` (incorrectly)  
- If hash differs → `sumdbMismatch` error  

#### Conclusion  
For `Client.Lookup("golang.org/x/bad", "v1.0.0")` in **Case B**:  
1. **Returns** the unauthenticated tree-note line (`golang.org/x/bad...`)  
2. **Error** = `nil`  
3. **cmd/go outcome**:  
   - `sumdbMismatch` if hashes differ  
   - Silent acceptance if attacker-forced hash matches  

**Root Cause**: Identity extraction scans the **entire HTTP payload** (including unauthenticated tree-note extensions) rather than the authenticated `text` body. Authentication (`checkRecord`) ignores tree-note content.  

**Recommendation**: Modify `Lookup` to scan only `text` (authenticated record) for identities, not full cache payload.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
