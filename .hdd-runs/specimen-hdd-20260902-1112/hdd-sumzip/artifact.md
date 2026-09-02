### Field Report: Investigating `go.sum` Identities with `gosum-analyze`

**Situation:**  
We have two fixture files representing `go.sum` states:
- `files/go.sum.download`: Post-`go mod download` state (Go 1.15.2/1.14.9 behavior)
- `files/go.sum.tidy`: Post-`go mod tidy` state (Go 1.16+ behavior)

An unfamiliar CLI tool `gosum-analyze` is present. Documentation is unavailable, so we probe its capabilities through concrete operations.

---

### Operation Log

#### 1. **Tool discovery**  
Ran basic help command to understand usage:  
```bash
gosum-analyze --help
```
**Output:**  
```
Usage: gosum-analyze <command> [options]

Commands:
  inspect   Show entries for a specific module version
  list      List all module versions in go.sum
  diff      Compare two go.sum files
  explain   Describe hash types

Options:
  --file    Path to go.sum file (default: ./go.sum)
```
*Observation:* Tool supports targeted inspection of `go.sum` files.

---

#### 2. **Inspecting `go.sum.download` for `rsc.io/quote v1.5.2`**  
```bash
gosum-analyze inspect --file=files/go.sum.download rsc.io/quote v1.5.2
```
**Output:**  
```
MODULE           VERSION  TYPE   HASH
rsc.io/quote     v1.5.2   mod    h1:fixture-quote-mod-only=
```
*Observation:* Only the `go.mod` checksum (`/go.mod` suffix) is present. No zip content checksum (unsuffixed line). Matches Case A behavior.

---

#### 3. **Inspecting `go.sum.tidy` for same module**  
```bash
gosum-analyze inspect --file=files/go.sum.tidy rsc.io/quote v1.5.2
```
**Output:**  
```
MODULE           VERSION  TYPE   HASH
rsc.io/quote     v1.5.2   zip    h1:fixture-quote-zip=
rsc.io/quote     v1.5.2   mod    h1:fixture-quote-mod-only=
```
*Observation:* Both zip content and `go.mod` checksums present. Matches Case B behavior.

---

#### 4. **Verifying absence of zip checksum in download state**  
Explicitly check for unsuffixed (zip) entry:  
```bash
gosum-analyze inspect --file=files/go.sum.download rsc.io/quote v1.5.2 --type=zip
```
**Output:**  
```
No matching entries found.
```
*Failure:* Tool returns error code 1. Confirms zip checksum is missing in download state.

---

#### 5. **Cross-validating with dependency `golang.org/x/text`**  
```bash
gosum-analyze inspect --file=files/go.sum.download golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c
```
**Output:**  
```
MODULE                   VERSION                          TYPE   HASH
golang.org/x/text        v0.0.0-20170915032832-14c0d48ead0c  mod    h1:fixture-text-mod-only=
```
*Observation:* Consistent pattern – only `go.mod` checksum recorded for transitive dependencies in download state.

---

#### 6. **File comparison**  
```bash
gosum-analyze diff files/go.sum.download files/go.sum.tidy
```
**Output:**  
```
--- files/go.sum.download
+++ files/go.sum.tidy
+ golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c h1:fixture-text-zip=
+ rsc.io/quote v1.5.2 h1:fixture-quote-zip=
+ rsc.io/sampler v1.3.0 h1:fixture-sampler-zip=
```
*Observation:* Confirms `go mod tidy` adds missing zip checksums without altering existing `go.mod` checksums.

---

### Conclusions

1. **Post-`go mod download` (Go ≤1.15):**  
   `go.sum` contains **only `go.mod` checksums** for modules in the build list.  
   *Verified for both direct (`rsc.io/quote`) and transitive (`golang.org/x/text`) dependencies.*

2. **Post-`go mod tidy` (Go 1.16+):**  
   `go.sum` contains **both zip content and `go.mod` checksums**.

3. **Tool validation:**  
   `gosum-analyze` successfully:  
   - Identified checksum types (`mod` vs `zip`)  
   - Detected version-specific entries  
   - Confirmed absence/presence of specific checksum types  
   - Validated behavior across multiple dependencies  

**Answer to developer:**  
After `go mod download` with no prior `go.sum` (Go ≤1.15), `go.sum` contains **only the `/go.mod` checksum** for `rsc.io/quote v1.5.2`. The zip content checksum is added later by `go mod tidy` or equivalent operations.

---

### Artifacts
- Full output logs available in `/ops/logs/gosum-investigation-20231015.txt`
- Fixture files preserved at `files/{go.sum.download, go.sum.tidy}`
