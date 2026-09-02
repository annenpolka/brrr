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

pytest's cache directory can keep the identity of an **already-initialized cache dir** after a write that only created the directory, even when the supporting files that mark that identity (`.gitignore`, `CACHEDIR.TAG`, `README.md`) were never written.

On failing_ref `4e3dd21506a9e543c04c63ebff966a9b604d2b9e`, `Cache.set` (`src/_pytest/cacheprovider.py`) decides whether to call `_ensure_supporting_files` with:

```
if path.parent.is_dir():
    cache_dir_exists_already = True
else:
    cache_dir_exists_already = self._cachedir.exists()
    path.parent.mkdir(exist_ok=True, parents=True)
if not cache_dir_exists_already:
    self._ensure_supporting_files()
```

`Cache.mkdir` creates `_cachedir/d/<name>` with `parents=True` and never calls `_ensure_supporting_files`. `_ensure_supporting_files` writes `README.md`, `.gitignore` (`# Created by pytest automatically.` plus `*`), and `CACHEDIR.TAG`.

Public report (pytest-dev/pytest#12167): the earlier check from PR 3982 is not robust. If a cache write is interrupted after the directory exists and is non-empty, `.pytest_cache` is present without `.gitignore`. Because `_cachedir.exists()` is then true, later `set` calls never write the supporting files.

Case A — first `Cache.set("cache/lastfailed", ...)` on an absent `.pytest_cache`:
  `path.parent` (`v/`) is not a dir
  `_cachedir.exists()` is false
  supporting files are written
  no leftover uninitialized dir identity

Case B — interrupt after `.pytest_cache/` (and maybe `v/`) exists, before supporting files:
  leftover: dir identity is "already initialized"
  `.gitignore` / `CACHEDIR.TAG` omitted
  later `set` sees exists() and skips `_ensure_supporting_files`

Case C — `Cache.mkdir("plugin-dump")` then `Cache.set(...)` with no interrupt:
  mkdir created `_cachedir` via `parents=True`
  set sees `_cachedir.exists()` true
  leftover: same omitted supporting-file identity as B, without a crash

Case D — `--cache-clear` then `set` on a missing dir:
  `clear_cache` removes the leftover dir
  not this leftover (fresh identity)

The developer wants to know which identity case B (and C) actually left for `.pytest_cache`: leftover "already initialized" dir (supporting files omitted), supporting-file identity present (`.gitignore` + `CACHEDIR.TAG`), or omitted (no cache dir at all).

# OBSERVED

Public pytest-dev/pytest#12167 (closed 2024-04-06). PR 12168 (tamird) merge `5acc3f86ac1713aea6775f04dcae35a2f0848437` (parents `4e3dd21506a9e543c04c63ebff966a9b604d2b9e` + `2e65f4e3ac81dd5e294839441262b8b112ba18bd`). Local pytest was not performed on this lab host.

Issue body: PR 3982's supporting-file write is gated on the cache directory not already existing. An interrupted cache write can leave `.pytest_cache` non-empty without `.gitignore`. The exists-already check then never creates `.gitignore`.

On failing_ref, `Cache.set` uses `path.parent.is_dir()` / `_cachedir.exists()` as the initialized-dir identity. `Cache.mkdir` does not call `_ensure_supporting_files`. `_ensure_supporting_files` is the only writer of `.gitignore` / `CACHEDIR.TAG` / `README.md`.

Atomic tempdir+rename of supporting files is **not** on the failing revision. It is added by PR 12168 (`_ensure_cache_dir_and_supporting_files`).

Not this packet: specimen-001 (assertion display evaluation order). specimen-002 (collection-identity / config-scope). specimen-003 (object-identity / fixture-closure). specimen-055 (derived rootdir collect). specimen-094 (vitest cache key). pytest#5702 / #3968 / #10002 / #14935 remain open (no merged fixed_ref). Coordinator skip of job-0371 as duplicate of 001-003 is the wrong object: those packets are assertion/collection/fixture identity, not leftover cache-dir vs supporting-file identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# src/_pytest/cacheprovider.py Cache.set / Cache.mkdir / _ensure_supporting_files

# public shape:
# Cache.mkdir or interrupted Cache.set leaves .pytest_cache existing
# later Cache.set: cache_dir_exists_already True
# leftover: .gitignore / CACHEDIR.TAG omitted
```

Source-backed only. Do not execute untrusted checkouts on the host.

pytest-dev/pytest
  src/_pytest/cacheprovider.py
  changelog/12167.trivial.rst

RELEVANT MATERIAL

### cacheprovider_set_failing.py

# Reduced excerpt of Cache.set / mkdir / _ensure_supporting_files on failing_ref
# src/_pytest/cacheprovider.py
# 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# Directory existence is the initialized-cache identity.
# Supporting files are written only when that identity is absent.

    def mkdir(self, name: str) -> Path:
        path = Path(name)
        if len(path.parts) > 1:
            raise ValueError("name is not allowed to contain path separators")
        res = self._cachedir.joinpath(self._CACHE_PREFIX_DIRS, path)
        res.mkdir(exist_ok=True, parents=True)
        return res

    def set(self, key: str, value: object) -> None:
        path = self._getvaluepath(key)
        try:
            if path.parent.is_dir():
                cache_dir_exists_already = True
            else:
                cache_dir_exists_already = self._cachedir.exists()
                path.parent.mkdir(exist_ok=True, parents=True)
        except OSError as exc:
            self.warn(
                f"could not create cache path {path}: {exc}",
                _ispytest=True,
            )
            return
        if not cache_dir_exists_already:
            self._ensure_supporting_files()
        data = json.dumps(value, ensure_ascii=False, indent=2)
        try:
            f = path.open("w", encoding="UTF-8")
        except OSError as exc:
            self.warn(
                f"cache could not write path {path}: {exc}",
                _ispytest=True,
            )
        else:
            with f:
                f.write(data)

    def _ensure_supporting_files(self) -> None:
        readme_path = self._cachedir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="UTF-8")
        gitignore_path = self._cachedir.joinpath(".gitignore")
        msg = "# Created by pytest automatically.\n*\n"
        gitignore_path.write_text(msg, encoding="UTF-8")
        cachedir_tag_path = self._cachedir.joinpath("CACHEDIR.TAG")
        cachedir_tag_path.write_bytes(CACHEDIR_TAG_CONTENT)

### leftover_identity_split.txt

Registry / fixture:
  cache_dir = .pytest_cache
  Cache.set / Cache.mkdir

Case A (first set, absent dir):
  supporting-file identity written
  no leftover uninitialized dir

Case B (interrupt after dir exists, no .gitignore):
  leftover: exists() identity
  .gitignore / CACHEDIR.TAG omitted

Case C (mkdir then set, no interrupt):
  mkdir created _cachedir via parents=True
  leftover: same omitted supporting files

Case D (--cache-clear then set):
  leftover dir removed
  not this leftover

Not this packet:
  assertion display evaluation order (specimen-001)
  collection-identity / config-scope (specimen-002)
  object-identity / fixture-closure (specimen-003)
  derived rootdir collect (specimen-055)
  vitest cache key (specimen-094)
  pytest#5702 / #3968 / #10002 / #14935 (open; no merged fixed_ref)

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

        ### Field Report: Investigating pytest Cache Directory Identity

**Objective:** Determine the identity state of `.pytest_cache` after interrupted writes (Case B) and `mkdir`-then-`set` operations (Case C) using source analysis and available CLI tools.

**Environment:** Pre-installed CLI tools (`git`, `python3`), source-backed inspection only (no execution of untrusted checkouts).

---

### Step 1: Verify Source Code Behavior
**Command:**  
```bash
git clone --no-checkout https://github.com/pytest-dev/pytest && \
cd pytest && \
git show 4e3dd21506a9e543c04c63ebff966a9b604d2b9e:src/_pytest/cacheprovider.py
```

**Output:**  
```python
# [...] (Excerpt matches provided cacheprovider_set_failing.py)
```

**Observation:**  
Confirmed `Cache.set` logic uses `path.parent.is_dir()` and `_cachedir.exists()` as gatekeepers for `_ensure_supporting_files`. `Cache.mkdir` lacks supporting file creation.

---

### Step 2: Simulate Case B (Interrupted Write)
**Procedure:**  
1. Create empty `.pytest_cache/v/` directory (simulates interrupt after dir creation)  
2. Run `Cache.set("key", value)` against this state  

**Simulated Code Path:**  
```python
path.parent.is_dir()  # True → cache_dir_exists_already = True
# SKIPS _ensure_supporting_files()
```

**Observation:**  
No supporting files written. `.pytest_cache` remains with directory structure but lacks `.gitignore`, `CACHEDIR.TAG`, `README.md`.

---

### Step 3: Simulate Case C (mkdir-then-set)
**Procedure:**  
1. Run `Cache.mkdir("plugin-dump")` → creates `.pytest_cache/d/plugin-dump`  
2. Run `Cache.set("key", value)`  

**Simulated Code Path:**  
```python
# During set():
path.parent.is_dir()  # False (v/ not created yet)
→ else branch:
self._cachedir.exists()  # True (root dir exists from mkdir)
cache_dir_exists_already = True  # SKIPS _ensure_supporting_files()
```

**Observation:**  
Identical to Case B: `.pytest_cache` directory exists with `d/plugin-dump` subdirectory but **no supporting files**.

---

### Step 4: Verify Atomic Write Absence
**Command:**  
```bash
git diff 4e3dd21506a9e543c04c63ebff966a9b604d2b9e..5acc3f86ac1713aea6775f04dcae35a2f0848437 -- src/_pytest/cacheprovider.py
```

**Output Excerpt:**  
```diff
+    def _ensure_cache_dir_and_supporting_files(self) -> None:
+        # Uses atomic write via temp dir
```

**Observation:**  
Atomic write mechanism **absent** in failing revision. Supporting files written directly to cache dir without transactional safety.

---

### Conclusion
**Identity State:**  
Both Case B (interrupted write) and Case C (`mkdir`-then-`set`) leave `.pytest_cache` in identical state:  
- **Directory exists:** `True` (via `_cachedir.exists()`)  
- **Supporting files present:** `False` (`.gitignore`, `CACHEDIR.TAG`, `README.md` missing)  

**Root Cause:**  
The cache directory's "initialized" identity is defined solely by its existence (`_cachedir.exists()`). Supporting files are **never** written if any prior operation (including partial/interrupted writes) creates the directory first.

**Recommendation:**  
PR #12168's atomic write solution addresses this by decoupling directory existence from supporting file integrity.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
