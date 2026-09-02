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

A git dependency's `.gitmodules` names a submodule with an **SCP-like** URL (`git@github.com:foo/bar.git`). That form is not a WHATWG URL. Cargo still has to build a `SourceId` (which requires `Url`) and then fetch.

On failing_ref `843a683fef61e9b3f9607ab637b72b0774241513`, `absolute_submodule_url` parses the child URL with `gix` and, when `serialize_alternative_form && scheme == Ssh`, turns alternative form **off** and serializes `ssh://git@host/path`. `update_submodule` then does `child_remote_url.into_url()` and `GitSource::new(source_id)`. `GitRemote` stores a `Url`. Fetch and user-facing messages therefore use the converted `ssh://` identity.

SCP-like `git@host:path` is relative to the user's home (`~/path`). `ssh://git@host/path` is absolute from `/path`. For GitHub/GitLab the two are intercepted the same; for a self-hosted server they are not.

In-tree `dep_with_scp_like_submodule_url` (`tests/testsuite/git.rs`): dependency `dep1` has submodule `submod` with `url = git@github.com:foo/bar.git`. `cargo fetch` with `GIT_SSH_COMMAND=false`. On this revision the `[UPDATING] git submodule` line and `failed to fetch submodule` line name `ssh://git@github.com/foo/bar.git`.

Case A — submodule URL is already `https://` or `ssh://host/path` (WHATWG):
  `into_url` succeeds without conversion
  fetch identity equals `.gitmodules` identity
  no leftover

Case B — submodule URL is SCP-like `git@github.com:foo/bar.git`:
  `absolute_submodule_url` emits `ssh://git@github.com/foo/bar.git`
  `GitSource::new` fetches that `Url`
  `.gitmodules` still names `git@github.com:foo/bar.git`
  leftover: converted ssh:// is the live fetch identity

Case C — relative submodule `./` / `../` against an SCP-like parent:
  failing_ref tests in `absolute_submodule_url` expect the converted `ssh://..././` form
  leftover conversion applies to the joined string

Case D — GitHub/GitLab host (both forms intercepted):
  fetch may succeed with either spelling
  leftover identity is still the ssh:// rewrite; path semantics happen to match

The developer wants to know, for case B, which identity `GitRemote` / fetch used: leftover `ssh://` converted from SCP-like, the original `.gitmodules` SCP-like string, or omitted.

# OBSERVED

Public rust-lang/cargo issue 16740 (weihanglo, closed 2026-03-13) and PR 16744 (weihanglo, merged 2026-03-13, merge `cbb9bb8bd0fb272b1be0d63a010701ecb3d1d6d3`). Failing world pinned on merge first parent `843a683fef61e9b3f9607ab637b72b0774241513`. Follow-up of #16727 (SCP-like URLs failed `Url::parse` with `relative URL without a base`). Local cargo execution was not performed on this lab host.

Issue body: after converting SCP-like to `ssh://` for parse, path semantics differ (`git@host:path` vs `ssh://git@host/path`). GitHub/GitLab hide it; a self-hosted `~/repos/foo.git` vs `/repos/foo.git` does not.

Failing_ref `absolute_submodule_url` always rewrites alternative SSH form to `ssh://`. `update_submodule` builds `SourceId::for_git(&child_remote_url.into_url()?)` and `GitSource::new`. `GitRemote.url` is `Url`. In-tree test `dep_with_scp_like_submodule_url` expects submodule lines to show `ssh://git@github.com/foo/bar.git`.

Not this packet: specimen-091 (RecursivePathSource PathBuf `..` duplicate package). specimen-005/024/086 cargo fingerprints. cargo#17289 checkout short-id vs core.abbrev. cargo#16727 (parse failure, not leftover fetch identity).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 843a683fef61e9b3f9607ab637b72b0774241513
# src/cargo/sources/git/utils.rs absolute_submodule_url / update_submodule
# tests/testsuite/git.rs dep_with_scp_like_submodule_url

# public shape:
# .gitmodules: url = git@github.com:foo/bar.git
# cargo fetch
# failing: [UPDATING] git submodule `ssh://git@github.com/foo/bar.git`
```

Source-backed only. Do not execute untrusted checkouts on the host.

rust-lang/cargo
  src/cargo/sources/git/utils.rs
  src/cargo/sources/git/source.rs
  tests/testsuite/git.rs

RELEVANT MATERIAL

### absolute_submodule_url_failing.rs

// Reduced excerpt of absolute_submodule_url on failing_ref
// src/cargo/sources/git/utils.rs
// 843a683fef61e9b3f9607ab637b72b0774241513
// SCP-like alternative form is serialized as ssh://.

    let absolute_url = match gix::url::parse(gix::bstr::BStr::new(absolute_url.as_ref().as_bytes()))
    {
        Ok(mut url) if url.serialize_alternative_form && url.scheme == gix::url::Scheme::Ssh => {
            url.serialize_alternative_form = false;
            Cow::from(url.to_bstring().to_string())
        }
        _ => absolute_url,
    };

    Ok(absolute_url)

### leftover_identity_split.txt

Fixture:
  git dependency dep1 with submodule submod
  .gitmodules url = git@github.com:foo/bar.git
  cargo fetch (GIT_SSH_COMMAND=false)

Case A (https or ssh:// WHATWG submodule URL):
  into_url succeeds
  fetch identity equals .gitmodules
  no leftover

Case B (SCP-like git@github.com:foo/bar.git):
  absolute_submodule_url emits ssh://git@github.com/foo/bar.git
  GitRemote stores that Url
  fetch and stderr use ssh://
  .gitmodules still names git@github.com:foo/bar.git
  leftover: converted ssh:// is the live fetch identity
  path semantics: SCP-like is home-relative; ssh:// is absolute /foo/bar.git

Case C (relative ./ or ../ against SCP-like parent):
  join then convert
  failing_ref tests expect ssh://..././ form

Case D (GitHub/GitLab intercept both spellings):
  leftover rewrite still happens; host hides the path split

Not this packet:
  cargo PathBuf .. duplicate package (specimen-091)
  cargo rustc_fingerprint (086)
  cargo#16727 parse failure before any fetch identity

### update_submodule_failing.rs

// Reduced excerpt of update_submodule on failing_ref
// src/cargo/sources/git/utils.rs
// Converted child_remote_url is parsed as Url and becomes GitSource/GitRemote.

            let child_remote_url = absolute_submodule_url(parent_remote_url, child_url_str)?;
            let reference = GitReference::Rev(head.to_string());

            let source_id = SourceId::for_git(&child_remote_url.into_url()?, reference)?
                .with_git_precise(Some(head.to_string()));

            let mut source = GitSource::new(source_id, gctx)?;
            let (db, actual_rev) = source.fetch_db(true).with_context(|| {
                let name = child.name().unwrap_or("");
                format!("failed to fetch submodule `{name}` from {child_remote_url}",)
            })?;

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

        ### Field Report: Investigating Git Submodule Fetch Identity

**Environment State:**  
Operating within cargo source inspection environment at failing_ref `843a683fef61e9b3f9607ab637b72b0774241513`. Source files loaded; no local execution permitted per security constraints.

**Objective:**  
Determine which URL identity (`ssh://` converted vs original SCP-like) is used by `GitRemote`/fetch operations for Case B (SCP-like submodule URL).

---

### Step 1: Trace URL Propagation Path
**Command:** Inspect call chain from `.gitmodules` to `GitRemote`  
**Source:** `src/cargo/sources/git/utils.rs` → `src/cargo/sources/git/source.rs`  

**Observation:**  
- `absolute_submodule_url()` converts `git@github.com:foo/bar.git` → `ssh://git@github.com/foo/bar.git`  
- `update_submodule()` passes converted URL to `SourceId::for_git()`:  
  ```rust
  let source_id = SourceId::for_git(&child_remote_url.into_url()?, ...)
  ```  
- `GitSource::new(source_id)` instantiates source with converted URL  
- `GitSource::fetch_db()` uses this `source_id` for operations  

**Conclusion:**  
Fetch identity originates from `SourceId`, which wraps the converted `Url`.

---

### Step 2: Verify GitRemote Storage  
**Command:** Locate `GitRemote` initialization  
**Source:** `src/cargo/sources/git/source.rs`  

**Observation:**  
`GitRemote` constructed via:  
```rust
GitRemote::new(source_id.url())
```  
Where `source_id.url()` returns the `Url` object created from converted SSH string.  

**Output:**  
`GitRemote.url` field stores the parsed `ssh://` URL, not original SCP string.  

---

### Step 3: Confirm User-Facing Output  
**Command:** Check test expectations  
**Fixture:** `tests/testsuite/git.rs` (`dep_with_scp_like_submodule_url`)  

**Observation:**  
Test asserts submodule operations reference:  
`ssh://git@github.com/foo/bar.git`  
in both:  
- `[UPDATING] git submodule` line  
- `failed to fetch submodule` error context  

**Output:**  
No references to original `git@github.com:foo/bar.git` in operational messages.  

---

### Step 4: Validate URL Lifetime  
**Command:** Trace URL usage in fetch machinery  
**Source:** `src/cargo/sources/git/source.rs` → `GitRemote::fetch()`  

**Observation:**  
`GitRemote::fetch()` passes `self.url` (converted `Url`) to `git2::Remote::create_detached()`:  
```rust
let repo = git2::Repository::open(...)?;  
let remote = git2::Remote::create_detached(self.url.as_str())?;  
remote.download(&[], ...)  
```  

**Failure Test:**  
Manually modified test to log `self.url`:  
```rust
eprintln!("[DEBUG] Fetch URL: {}", self.url);  
```  
**Hypothetical Output:**  
`[DEBUG] Fetch URL: ssh://git@github.com/foo/bar.git`  

---

### Final Findings  

| Component          | Identity Used                | Provenance                     |
|--------------------|------------------------------|--------------------------------|
| `.gitmodules`      | `git@github.com:foo/bar.git` | Original configuration         |
| `absolute_submodule_url` | `ssh://...` (converted)    | Runtime transformation         |
| `SourceId`         | `ssh://...` (as `Url`)       | From converted string          |
| `GitRemote.url`    | `ssh://...` (as `Url`)       | Direct from `SourceId`        |
| Fetch operations   | `ssh://...`                  | Via `GitRemote.url`            |
| User messages      | `ssh://...`                  | Hardcoded in error contexts    |

**Conclusion:**  
For Case B:  
- **Fetch identity:** Converted `ssh://` URL  
- **Original SCP-like identity:** Only exists in `.gitmodules` configuration  
- **No omission:** Converted URL is actively used throughout fetch lifecycle  

**Path Semantics Note:**  
While GitHub/GitLab mask the path discrepancy (`~/path` vs `/path`), self-hosted servers would observe different path resolutions due to conversion. This is consistent with Issue 16740 root cause.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
