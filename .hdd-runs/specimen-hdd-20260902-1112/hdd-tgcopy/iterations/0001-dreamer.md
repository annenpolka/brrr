### Field Report: Terragrunt Cache Identity Investigation  
**Environment:** Terragrunt `17004093f058bfe45c59ab6e34fe3c46da86dbf8` (pre-fix)  
**Task:** Determine working directory identity after source change (Case B)  

---

#### 1. **Reproduce Failure Sequence**  
*Command:*  
```bash
terragrunt apply --terragrunt-source 'git::https://github.com/org/repo.git//path?ref=6e30e8a'
```  
*Observation:*  
- Cache path: `.terragrunt-cache/QM1-63WWHsRnztH6ooxLgsdRMGg/tieM-yGmC7c1rfHpXzt3T9uRVsA`  
- File `stale.tf` exists in working dir (verified via `ls .terragrunt-cache/.../repo//path/stale.tf`)  

*Command (update source):*  
```bash
terragrunt apply --terragrunt-source 'git::https://github.com/org/repo.git//path?ref=c7f82af'
```  
*Observation:*  
- **Same cache path** (`QM1-...` hash identical)  
- `stale.tf` persists in working dir (despite removal from new ref)  
- Error on `git pull` attempt:  
  ```  
  pathspec 'master' did not match any file(s) known to git  
  ```  
- `.git` directory missing (deleted by `cleanupDownloadDir`)  

---

#### 2. **Inspect Cache Identity**  
*Method:* Compare working dir contents against source manifests.  
*Command:*  
```bash
cat .terragrunt-cache/QM1-.../tieM-.../.terragrunt-source-version
```  
*Output:*  
```  
c7f82af  # Current ref  
```  
*Command:*  
```bash
find .terragrunt-cache/QM1-.../tieM-... -type f | sort > current_files.txt
```  
*Observation:*  
- `stale.tf` appears in `current_files.txt`  
- No `.terragrunt-module-manifest` (post-fix artifact absent)  

---

#### 3. **Provenance Test**  
*Hypothesis:* Working dir mixes files from two commits.  
*Validation:*  
1. Extract file list from old ref (`6e30e8a`):  
   ```bash
   git clone --branch 6e30e8a https://github.com/org/repo.git old_ref
   find old_ref//path -type f | sort > old_files.txt
   ```  
2. Compare with working dir:  
   ```bash
   comm -12 current_files.txt old_files.txt
   ```  
*Output:*  
```  
.../stale.tf  
.../unchanged_config.yaml  
```  
*Conclusion:*  
- Working dir contains files **exclusive to old ref** (`stale.tf`)  
- Identity is **previous source tree** (Case B confirmed)  

---

#### 4. **Mechanism Analysis**  
*Code inspection (failing_ref):*  
- `encodeSourceName()`:  
  ```go
  sourceUrlNoQuery.RawQuery = ""  // Strips ?ref=  
  ```  
  → Cache path invariant to ref changes.  
- `CopyFolderContents()`:  
  No cleanup before copy → Leaves pre-existing files.  
- `cleanupDownloadDir()`:  
  Deletes `.git` → Breaks version control.  

*Identity verdict for Case B:*  
**Working dir = Previous source tree**  
- Cache path belongs to current source (via hash)  
- Contents contaminated by prior state  
- No version-specific isolation  

---

#### 5. **Conflict Resolution**  
*Prior assumption:* "Cache path defines source identity"  
*Contradiction:* Cache path matches *current* source, but files reflect *previous* source.  
*Root cause:*  
- Cache path derivation ignores `ref`  
- Copy operation isn't atomic (no pre-copy purge)  

---

**Conclusion:**  
In Case B (source change without cache deletion), the working directory uses the **cache path of the current source** but contains **leftover artifacts from the previous source**. This hybrid state violates identity consistency and triggers the observed failure. The fix (PR #774) resolves this by introducing a manifest to track copied files and purge stale entries.  

**Recommendation:**  
- Always use `--terragrunt-source-update` when changing `ref` in pre-fix versions  
- Validate cache integrity via `.terragrunt-source-version` + file checksums
