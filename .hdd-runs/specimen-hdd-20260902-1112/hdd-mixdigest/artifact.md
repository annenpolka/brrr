### Field Report: Investigating Elixir Compiler Identity Case B  

**Tool Environment:**  
- Active CLI: `mix_analyzer` (version 1.3.2)  
- Mode: Static code analysis (no execution of untrusted checkouts)  
- Loaded artifacts:  
  - `elixir_compile_failing.ex` (excerpt from failing_ref)  
  - `leftover_identity_split.txt` (case definitions)  

---

#### Step 1: Inspect Stale Detection Logic  
**Command:**  
```bash  
mix_analyzer parse-condition --file elixir_compile_failing.ex --line 5  
```  
**Output:**  
```  
Condition:  
  (size != last_size)  
  OR Mix.Utils.stale?([last_mtime | times], [modified])  
  OR Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1))  
```  
**Observation:**  
The condition depends on three mutually reinforcing checks:  
1. Source `size` change  
2. File mtime freshness  
3. Dependency recompilation flags  

---

#### Step 2: Simulate Case B Parameters  
**Command:**  
```bash  
mix_analyzer simulate-case \  
  --case B \  
  --size 100 \  
  --last_size 100 \  
  --last_mtime "2021-06-01T10:00:00Z" \  
  --modified "2021-06-01T10:00:00Z" \  # Reset future mtime → now  
  --modules_to_recompile "[]"  
```  
**Output:**  
```  
[OUTCOME]  
- Size check: MATCH (100 == 100) → false  
- Mtime check: Mix.Utils.stale?([2021-06-01T10:00:00Z], [2021-06-01T10:00:00Z]) → false  
- Module recompilation check: false  
→ Source marked UNCHANGED. No recompile triggered.  
```  
**Failure:**  
Output lacks BEAM identity metadata. Need deeper artifact inspection.  

---

#### Step 3: Query BEAM Provenance Mechanism  
**Command:**  
```bash  
mix_analyzer beam-provenance \  
  --case B \  
  --assume_unchanged \  
  --previous_beam_hash "sha256:9f86d081"  
```  
**Output:**  
```  
[PROVENANCE TRACE]  
- Module loader: BEAM identity derived SOLELY from:  
  1. File path (/build/lib/module.beam)  
  2. Embedded {:source, size, mtime} metadata (size=100, mtime=2021-06-01T10:00:00Z)  
- NO content digest check performed.  
- NO invalidation of previous BEAM (hash: sha256:9f86d081).  
```  
**Observation:**  
After same-length rewrite (Case B):  
- Compiler uses **leftover previous BEAM** (identified by path + stale metadata).  
- Source bytes are **not consulted** (no digest exists in source record).  
- Compile cache is **omitted** (no recompilation occurred).  

---

#### Step 4: Verify Against Repaired Implementation  
**Command:**  
```bash  
mix_analyzer compare-case \  
  --case B \  
  --case D \  
  --diff-field source.digest  
```  
**Output:**  
```  
[DIFF]  
- Case B (failing_ref): source record → {size, mtime}  
- Case D (repaired): source record → {digest, mtime}  
  
[EFFECT]  
Case B: BEAM identity = f(path, last_size, last_mtime) → STALE after rewrite  
Case D: BEAM identity = f(path, content_digest) → INVALIDATED after rewrite  
```  

---

#### Conclusion: Case B Identity  
- **Leftover previous BEAM** was used post-rewrite.  
- Root cause: Identity binding relied on `{path, size, mtime}` tuple, which became stale when:  
  - Size remained constant  
  - Mtime reset masked timestamp changes  
- Mitigation (confirmed in public report): Digest-based content checking replaces size.  

**Unresolved Uncertainty:**  
Tool cannot verify if BEAM loader *always* ignores source bytes in Case B without live `:code` inspection.  

**Recommendation:**  
Cross-verify with `mix_analyzer beam-loader-trace` on trusted fixture (not present in environment).
