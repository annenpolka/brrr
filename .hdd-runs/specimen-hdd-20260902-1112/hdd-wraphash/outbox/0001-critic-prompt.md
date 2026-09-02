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

Meson wrap resolution can keep the identity of a **previous wrap-file checkout** after the wrap file on disk has a new revision / source_hash / directory. If `subprojects/<dir>/meson.build` already exists, `Resolver.resolve` returns that leftover directory and does not compare wrap-file identity.

On failing_ref `97f248db24fe88495dbe35bbae6eafd643c0c94b`, `PackageDefinition` has no `wrapfile_hash`. There is no `.meson-subproject-wrap-hash.txt`. `resolve` is:

```
# The directory is there and has meson.build? Great, use it.
if method == 'meson' and os.path.exists(meson_file):
    return rel_path
```

Wrap-file contents (revision, source_url, source_hash, directory) are not that identity. Leftover checkout from the previous wrap file is kept.

Public report (mesonbuild/meson#10348): change wrap-file version/revision; ninja does not reconfigure; leftover subproject stays. meson#10159 (CI packagecache leftover across wrap-file updates) closed without a PR.

In-tree after the repair (not on failing_ref): `wrapfile_hash` SHA-256 of the wrap file; `update_hash_cache` writes `.meson-subproject-wrap-hash.txt`; `validate()` warns when stored hash ≠ current wrap-file hash. Unit test `test_wrap_git` changes `revision = master` to `not-master` and expects `revision may be out of date` on `--reconfigure`.

Case A — first `meson setup`, wrap matches the checkout just fetched:
  no leftover
  wrap-hash omitted (file does not exist yet)

Case B — wrap file edited (new revision / source_hash), leftover `subprojects/<dir>/meson.build`:
  leftover: previous wrap-file checkout
  current wrap-file identity is the new revision
  resolve returns leftover directory
  no wrap-hash compare

Case C — delete `subprojects/<dir>` then setup:
  fresh fetch from current wrap file
  not leftover checkout

Case D — cmake method with leftover directory (`CMakeLists.txt` present):
  leftover cmake checkout used
  same omitted wrap-file identity (meson path is the reported one)

The developer wants to know which identity case B actually used for the subproject: leftover previous wrap-file checkout, current wrap-file identity, or omitted (no subproject directory).

# OBSERVED

Public mesonbuild/meson#10348 (closed 2022-09-19). PR 10728 commit `004575874ffdb77ee997f9c19e0a041d144994d6` (parent `97f248db24fe88495dbe35bbae6eafd643c0c94b`). meson#10159 closed without a pull request. Local meson was not performed on this lab host.

Issue body: changing wrap-file contents does not trigger rebuild/reconfigure of the subproject.

On failing_ref, `resolve` treats an existing `meson.build` as identity. Wrap-file hash is not computed. `.meson-subproject-wrap-hash.txt` is not written. `update_hash_cache` / `validate` are **not** on the failing revision. They are added by PR 10728.

Not this packet: specimen-064/070/092 (nix NAR hash leftover vs rev). Distinct leftover: wrap-file identity vs leftover subproject checkout with wrap-hash omitted.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 97f248db24fe88495dbe35bbae6eafd643c0c94b
# mesonbuild/wrap/wrap.py Resolver.resolve

# public shape:
# leftover subprojects/<dir>/meson.build from previous wrap
# wrap file now has a different revision
# meson setup / ninja does not pick up wrap-file identity
```

Source-backed only. Do not execute untrusted checkouts on the host.

mesonbuild/meson
  mesonbuild/wrap/wrap.py
  mesonbuild/msubprojects.py
  unittests/allplatformstests.py
  subprojects/<dir>/.meson-subproject-wrap-hash.txt

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  subprojects/wrap_git.wrap revision = master then not-master
  leftover subprojects/<dir>/meson.build
  no .meson-subproject-wrap-hash.txt on failing_ref

Case A (first meson setup):
  checkout matches wrap
  wrap-hash omitted (no file)

Case B (wrap file edited, leftover meson.build):
  leftover: previous wrap-file checkout
  current wrap-file identity is new revision
  resolve returns leftover directory

Case C (delete subprojects/<dir> then setup):
  fresh fetch
  not leftover checkout

Case D (cmake leftover CMakeLists.txt):
  leftover cmake checkout
  wrap-file identity still omitted

Not this packet:
  nix NAR leftover vs rev (specimen-064/070/092)
  meson#10159 CI packagecache discussion (no PR)

### wrap_resolve_failing.py

# Reduced excerpt of Resolver.resolve on failing_ref
# mesonbuild/wrap/wrap.py
# 97f248db24fe88495dbe35bbae6eafd643c0c94b
# Existing meson.build is the identity. Wrap-file hash is omitted.

        meson_file = os.path.join(self.dirname, 'meson.build')
        cmake_file = os.path.join(self.dirname, 'CMakeLists.txt')

        # The directory is there and has meson.build? Great, use it.
        if method == 'meson' and os.path.exists(meson_file):
            return rel_path
        if method == 'cmake' and os.path.exists(cmake_file):
            return rel_path

# PackageDefinition.__init__ has no wrapfile_hash.
# get_hashfile / update_hash_cache / validate do not exist.

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

        ### Field Report: Investigating Meson Wrap Resolution Identity  

**Tool Used:** `meson-inspect` (version 0.62.0-dev, CLI for Meson build system introspection)  
**Objective:** Determine which identity is used for subprojects in Case B (leftover `meson.build` exists after wrap-file revision change).  

---

#### Step 1: Verify Environment State  
Command:  
```bash  
meson-inspect environment --current  
```  

Output:  
```  
[wrap-resolver]  
state: pre-hash-validation  
wrapdb_version: 97f248db24fe88495dbe35bbae6eafd643c0c94b  
identity_checks: absent  
```  
Observation: Confirms environment matches `failing_ref` (no wrapfile_hash validation).  

---

#### Step 2: Simulate Case B Scenario  
Created fixture:  
- `subprojects/pkg.wrap`: Initial revision `v1.0` → Changed to `v2.0`  
- Leftover `subprojects/pkg/meson.build` from `v1.0`  
- No `.meson-subproject-wrap-hash.txt`  

Command (attempt reconfigure):  
```bash  
meson-inspect wrap resolve pkg --method=meson  
```  

Output:  
```  
[Resolver]  
status: used_existing  
path: subprojects/pkg  
reason: "meson.build present"  
identity: no_validation_performed  
```  

Observation: Resolver explicitly returns leftover directory without checking wrap-file contents.  

---

#### Step 3: Trace Resolver Logic  
Command (source inspection):  
```bash  
meson-inspect code extract wrap.py --function=Resolver.resolve --lines=215-230  
```  

Output:  
```python  
# [EXCERPT] mesonbuild/wrap/wrap.py @ 97f248d  
def resolve(self):  
    meson_file = os.path.join(self.dirname, 'meson.build')  
    if method == 'meson' and os.path.exists(meson_file):  
        return rel_path  # <-- CASE B EXIT POINT  
    # ... (no hash checks present)  
```  

Observation: Code path shows unconditional return when `meson.build` exists. No revision/source_hash comparisons.  

---

#### Step 4: Check PackageDefinition Initialization  
Command:  
```bash  
meson-inspect code extract msubprojects.py --class=PackageDefinition  
```  

Output:  
```python  
class PackageDefinition:  
    def __init__(self, fname, subproject):  
        self.filename = fname  
        # ...  
        self.wrapfile_hash = None  # <-- ALWAYS UNSET  
```  

Observation: `wrapfile_hash` attribute exists but is never populated. Confirms absence of identity tracking.  

---

#### Step 5: Validate Against Fixed Version  
Command (compare with post-PR10728):  
```bash  
meson-inspect diff 97f248d..0045758 --file=wrap.py  
```  

Output excerpt:  
```diff  
+ if os.path.exists(hashfile):  
+     self.validate()  # Added in fix  
```  
Observation: Hash validation logic missing in failing_ref. Confirms resolution relies solely on directory presence.  

---

### Conclusion  
**Identity Used in Case B:** Leftover previous wrap-file checkout.  

**Evidence Chain:**  
1. Resolver returns early when `meson.build` exists (no wrap-file inspection).  
2. `PackageDefinition` contains no mechanism to store wrap-file identity.  
3. `.meson-subproject-wrap-hash.txt` handling absent in codebase.  
4. Reconfigure succeeds without fetching new revision.  

**Unresolved Uncertainty:**  
- Cannot verify if CMake method (Case D) behaves identically without test fixture.  
- Impact on transitive dependencies remains unobserved.  

**Recommended Next Command:**  
```bash  
meson-inspect wrap simulate --case=cmake_leftover  
```  
To verify consistency across method types.  

---  
*Report generated by meson-inspect v0.62.0-dev. Environment state persisted.*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
