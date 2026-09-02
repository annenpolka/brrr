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

Terragrunt `.terragrunt-cache` can keep the identity of a **previous source tree** after `terraform { source = "...?ref=..." }` changed. Two leftovers share one download folder:

1. `encodeSourceName` hashes the source URL **without the query string**. Different `ref=` values reuse `QM1-63WWHsRnztH6ooxLgsdRMGg/tieM-yGmC7c1rfHpXzt3T9uRVsA`. Version lives only in `.terragrunt-source-version`.
2. `CopyFolderContents` copies into that folder with **no manifest**. After source update, leftover `stale.tf` from the previous tree stays. `cleanupDownloadDir` then deletes leftover dest contents including `.git`, so go-getter `git pull` fails (`pathspec 'master' did not match`).

On failing_ref `17004093f058bfe45c59ab6e34fe3c46da86dbf8`:

```
func encodeSourceName(sourceUrl *url.URL) (string, error) {
	sourceUrlNoQuery, err := parseSourceUrl(sourceUrl.String())
	sourceUrlNoQuery.RawQuery = ""
	return util.EncodeBase64Sha1(sourceUrlNoQuery.String()), nil
}
func CopyFolderContents(source string, destination string) error {
	return CopyFolderContentsWithFilter(source, destination, func(path string) bool {
		return !PathContainsHiddenFileOrFolder(path)
	})
}
```

Public report (gruntwork-io/terragrunt#764). Change `?ref=` from `6e30e8a` to `c7f82af`; same cache path; leftover dest; delete `.terragrunt-cache` to get the new commit. In-tree test after the repair: `test-stale-file-exists` then `test-stale-file-doesnt-exist-after-source-update`.

In-tree after the repair (not on failing_ref): `.terragrunt-module-manifest` / `.terragrunt-source-manifest`; `CopyFolderContents(..., manifestFile)` Clean() previous copies; `cleanupDownloadDir` removed.

Case A — second run, same `source` / same files:
  cache identity is current
  not leftover-after-source-change

Case B — `ref=` or local files flipped, leftover dest:
  leftover: previous `stale.tf` / previous clone path
  ref omitted from cache-path identity
  same encoded folder

Case C — `rm -rf .terragrunt-cache` / `--terragrunt-source-update`:
  fresh source identity
  not leftover previous tree

Case D — copy manifest Clean() before recopy (post-repair shape, not on failing_ref):
  stale.tf gone after source update
  not leftover previous files

The developer wants to know which identity case B actually used for the working dir after the source change: leftover previous-copy (no manifest; ref omitted from path), current source identity, or omitted (no cache).

# OBSERVED

Public gruntwork-io/terragrunt#764 (closed 2019-07-31). PR 774 merge `85f63b2bbde2fc8d9b207799e6891c171e6527ee` (first parent `17004093f058bfe45c59ab6e34fe3c46da86dbf8`). Local terragrunt was not performed on this lab host.

Issue body: changing `...?ref=` keeps the same `.terragrunt-cache` hash subdirs; leftover dest; `git pull` fails after cleanup deleted `.git`; deleting the cache folder pulls the new commit.

On failing_ref, encodeSourceName omits query/ref from the cache path. CopyFolderContents has no list of previously copied files, so leftover `stale.tf` survives a source update. PR 774 tests `test-stale-file-doesnt-exist-after-source-update`.

Not this packet: specimen-118 terraform leftover identity omitted from apply state. terragrunt#6468 leftover deleted git-module files still OPEN (not this merged pair). PR 4781 catalog `ref != ""` one-line flip is THIN_WRAPPER, not packed.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 17004093f058bfe45c59ab6e34fe3c46da86dbf8
# cli/download_source.go encodeSourceName / CopyFolderContents / cleanupDownloadDir

# public shape:
# leftover .terragrunt-cache path after ?ref= change
# encodeSourceName omits query; leftover stale.tf; leftover dest without .git
# rm -rf .terragrunt-cache yields the new source
```

Source-backed only. Do not execute untrusted checkouts on the host.

gruntwork-io/terragrunt
  cli/download_source.go
  util/file.go

RELEVANT MATERIAL

### encode_source_failing.go

// Reduced excerpt of cache-path identity + copy on failing_ref
// cli/download_source.go / util/file.go
// 17004093f058bfe45c59ab6e34fe3c46da86dbf8
// encodeSourceName omits query/ref. CopyFolderContents has no manifest.

func encodeSourceName(sourceUrl *url.URL) (string, error) {
	sourceUrlNoQuery, err := parseSourceUrl(sourceUrl.String())
	sourceUrlNoQuery.RawQuery = ""
	return util.EncodeBase64Sha1(sourceUrlNoQuery.String()), nil
}

func CopyFolderContents(source string, destination string) error {
	return CopyFolderContentsWithFilter(source, destination, func(path string) bool {
		return !PathContainsHiddenFileOrFolder(path)
	})
}
// leftover previous files in destination after source change

### leftover_identity_split.txt

Registry / fixture:
  .terragrunt-cache download dir
  leftover previous source after ?ref= / file change

Case A (second run, same source):
  current cache identity
  not leftover-after-source-change

Case B (ref= or files flipped, leftover dest):
  leftover: previous stale.tf / previous clone path
  ref omitted from encodeSourceName
  same encoded folder

Case C (rm -rf .terragrunt-cache / --terragrunt-source-update):
  fresh source identity
  not leftover previous tree

Case D (copy manifest Clean before recopy):
  stale.tf gone after source update
  not leftover previous files

Not this packet:
  terraform leftover identity omitted from apply state (specimen-118)
  terragrunt#6468 leftover deleted git-module files (OPEN)

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
