### Field Report: Investigation of `bytesInOutput` Behavior in esbuild (failing_ref)

**Current Environment**:  
esbuild v0.14.38 (failing_ref `0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff`)  
Metafile enabled (`--metafile`), CSS/JS with `file`/`copy` loaders  
Operations performed via CLI and test snapshots  

---

#### 1. **Case A: CSS Without `url()` (Baseline)**  
**Command**:  
```bash
esbuild style.css --bundle --outdir=out --metafile=meta.json
```  
**Input File**: `style.css`  
```css
/* No asset references */
div { color: red; }
```  
**Observation**:  
```json
// meta.json
"outputs": {
  "out/style.css": {
    "inputs": {
      "style.css": { "bytesInOutput": 22 }
    },
    "bytes": 22
  }
}
```  
**Conclusion**:  
- `bytesInOutput` = `bytes` (22).  
- Matches printed CSS length. No placeholders involved.  

---

#### 2. **Case B: CSS `url()` with File Loader (No `publicPath`)**  
**Command**:  
```bash
esbuild styles.css --bundle --outdir=dist --metafile=meta.json --loader:.svg=file
```  
**Input File**: `styles.css`  
```css
body { background-image: url(./image.svg); }
```  
**Observation**:  
```json
// meta.json
"outputs": {
  "dist/styles.css": {
    "inputs": {
      "styles.css": { "bytesInOutput": 61 }
    },
    "bytes": 94
  }
}
```  
**Analysis**:  
- Printer output (pre-substitution): `body{background-image:url(<25-byte uniqueKey>);}` → Length **61**.  
- Final output (post-substitution): `body{background-image:url(image-WFRGLPG5.svg);}` → Length **94**.  
- **Discrepancy**: `bytesInOutput` locked to placeholder length (61 ≠ 94).  

---

#### 3. **Case C: CSS `url()` with `publicPath`**  
**Command**:  
```bash
esbuild styles.css --bundle --outdir=dist --metafile=meta.json --loader:.svg=file --public-path=/assets/
```  
**Observation**:  
```json
// meta.json
"outputs": {
  "dist/styles.css": {
    "inputs": {
      "styles.css": { "bytesInOutput": 61 }
    },
    "bytes": 102
  }
}
```  
**Analysis**:  
- Final output: `body{background-image:url(/assets/image-WFRGLPG5.svg);}` → Length **102**.  
- `bytesInOutput` unchanged (61) despite final URL growth.  
- **Pattern**: Substitution-specific changes (`publicPath`, asset names) ignored by `bytesInOutput`.  

---

#### 4. **Case D: In-Tree Test (99-Char Asset Name)**  
**Test Execution**:  
```bash
go test ./internal/bundler -run TestMetafileVeryLongExternalPaths
```  
**Snapshot Observation**:  
```json
// snapshots_default.txt
"out/bytesInOutput should be at least 99.css": {
  "inputs": {
    "project/bytesInOutput should be at least 99.css": {
      "bytesInOutput": 52
    }
  },
  "bytes": 196
}
```  
**Breakdown**:  
- Input CSS: `a { background: url(<99-four-chars>.file); }`  
- Printer output: `a{background:url(<25-byte uniqueKey>);}` → Length **52**.  
- Final output: `a{background:url(./444…99-four-chars…-55DNWN2R.file);}` → Length **196**.  
- **Delta**: 144 bytes unaccounted for in `bytesInOutput`.  

---

#### 5. **Case E: JS File Loader**  
**Input File**: `script.js`  
```javascript
import asset from './long-asset-name.file';
```  
**Observation**:  
```json
// meta.json (JS entry)
"outputs": {
  "out/script.js": {
    "inputs": {
      "script.js": { "bytesInOutput": 45 },
      "long-asset-name.file": { "bytesInOutput": 0 }
    },
    "bytes": 120
  }
}
```  
**Analysis**:  
- Printer output: `import"<25-byte uniqueKey>";` → Length **45**.  
- Final output: `import"./444…-55DNWN2R.file";` → Length **120**.  
- **Consistency**: JS exhibits same placeholder retention as CSS.  

---

### Key Findings  

1. **Placeholder Identity**:  
   - `bytesInOutput` records length **at compilation**, using `len(compileResult.CSS/JS)`.  
   - Contains `url(<uniqueKey>)` strings (25 bytes), not final paths.  

2. **Substitution Blindspot**:  
   - Changes to `publicPath`, `--asset-names`, or final path length **do not affect** `bytesInOutput`.  
   - Example:  
     - Placeholder: `url(uniqueKey)` (25 bytes).  
     - Final path: `url(/path/asset-HASH.ext)` (40 bytes).  
     - `bytesInOutput` reports 25; `bytes` reports 40 + deltas.  

3. **Provenance**:  
   - Confirmed in code:  
     - `bundler/linker.go`: `bytesInOutput = len(compileResult.CSS)` (pre-substitution).  
     - `file_loader_uniquekey.go`: Generates 25-byte `uniqueKey` placeholder.  
   - No remapping occurs between compilation and final output.  

4. **Failure Scope**:  
   - Occurs when:  
     - CSS `url()` or JS `file`/`copy` loader triggers placeholder.  
     - Path substitution modifies output length.  
   - Does not occur when:  
     - No assets referenced (Case A).  
     - Assets referenced but no path substitution (e.g., inline data-URLs).  

---

### Uncertainty  
- **Exact Delta Calculation**:  
  While `bytesInOutput` consistently reflects placeholder length (25 bytes per occurrence), the precise delta between it and `bytes` depends on:  
  - Number of asset references.  
  - Length of final paths (determined by `publicPath`, hashing, base names).  
  - Cannot derive formula without post-substitution byte tracking.  

**Recommendation**:  
Treat `bytesInOutput` as a pre-substitution value in builds with path-dependent asset loaders. Rely on `bytes` for final output size.
