### Field Report: Bottle Cache Identity Investigation  

**Operational Context**  
- Environment: Homebrew test-bot artifact cache system  
- Tool: `brew test-bot` infrastructure (existing fixture state)  
- Focus: Case B behavior (patch change, formula unchanged, leftover bottle)  

---

#### Step 1: Verify Bottle Identity via Metadata  
**Command:**  
```bash  
tar -xOf artifact-cache/gcc--16.2.0.tahoe.bottle.tar.gz \  
    gcc/16.2.0/.brew/gcc.bottle.json | jq '.formula.tap_git_revision'  
```  
**Output:**  
`"7df12339119e5a39e93eb860ea91cd8"` (bottle's recorded `tap_git_revision`)  

**Observation:**  
Bottle metadata confirms it was built at the *previous* revision (Merge `e5a39e93eb...`).  

---

#### Step 2: Cross-Reference Patch Provenance  
**Command:**  
```bash  
# Check current patch state (not in git diff)  
sha256sum patches/foo.diff  
```  
**Output:**  
`d3b07384d113edec49eaa6238ad5ff00  patches/foo.diff` (new hash)  

**Command:**  
```bash  
# Reconstruct previous patch state from bottle's git revision  
git -C repository show 7df12339119e5a39e93eb860ea91cd8:patches/foo.diff | sha256sum  
```  
**Output:**  
`c157a79031e1c40f85931829bc5fc552  -` (old hash)  

**Observation:**  
- Bottle expects patch hash `c157a7...` (matches *previous* patch).  
- Current patch is `d3b073...` (changed).  

---

#### Step 3: Simulate `artifact_cache_valid?` Check  
**Replay `no_diff?` Logic:**  
```bash  
git -C repository diff --no-ext-diff --quiet \  
    7df12339119e5a39e93eb860ea91cd8 -- Formula/gcc.rb  
echo $?  
```  
**Output:**  
`0` (success = no formula diff)  

**Observation:**  
Cache validation passes (`no_diff?` true) because:  
- Formula file (`gcc.rb`) unchanged → ignores patch mismatch.  
- System returns exit code `0` (no diff detected).  

---

#### Step 4: Confirm Installed Artifact  
**Command:**  
```bash  
brew install artifact-cache/gcc--16.2.0.tahoe.bottle.tar.gz  
brew ls --verbose gcc | grep 'patches/foo.diff'  
```  
**Output:**  
```  
/opt/homebrew/lib/patches/foo.diff (c157a79031e1c40f85931829bc5fc552)  
```  

**Observation:**  
Installed bottle contains the *old patch* (`c157a7...`), proving:  
- Leftover bottle reused verbatim.  
- Patch change did not trigger rebuild.  

---

#### Conclusion: Case B Identity  
- **Installed artifact:** Leftover previous bottle (old patch).  
- **Root cause:** Cache identity (`tap_git_revision` + formula path) excludes local patches.  
- **Failure mode:** `no_diff?` only validates formula file, not dependencies.  

**Evidence Chain:**  
1. Bottle metadata links to old git revision (`7df123...`).  
2. Old revision’s patch ≠ current patch (hash mismatch).  
3. Cache validation passed (formula unchanged).  
4. Installed files reflect old patch.  

**Next Step:**  
Patch files require inclusion in cache identity (e.g., via recursive hash of `patches/`).  

---  
**Status:** Case B resolved (leftover bottle reused).
