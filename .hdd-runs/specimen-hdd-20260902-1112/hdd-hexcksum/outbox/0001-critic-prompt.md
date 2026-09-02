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

Hex `Hex.SCM.fetch` can keep the identity of a **previous cached tarball** after the registry checksum changed (`mix hex.publish --replace`) and `mix deps.get` should have fetched a different package. The cache path is `~/.hex/packages/<repo>/<package>-<version>.tar`. Fetch only matches exact `outer_checksum` or `{:error, _}`. A cached tarball whose checksum differs from the registry is leftover previous package-version identity (CaseClauseError; workaround `rm` the tarball).

On failing_ref `6639c0ad8921fdaf0468d86cc51525c8237e357a`:

```
outer_checksum = Registry.outer_checksum(repo, package, version)
path = cache_path(repo, package, version)

case Hex.Tar.outer_checksum(path) do
  {:ok, ^outer_checksum} ->
    {:ok, :cached}

  {:error, _reason} ->
    case Hex.Repo.get_tarball(repo, package, version) do
      {:ok, {200, body, _headers}} ->
        File.mkdir_p!(Path.dirname(path))
        File.write!(path, body)
        {:ok, :new}
      ...
    end
end
```

`{:ok, other_outer_checksum}` is not a clause. Cache identity is package+version path, not registry checksum.

Public report (hexpm/hex#821). Publish; deps.get caches tarball; republish `--replace` so checksum changes; second deps.get CaseClauseError on leftover cached bytes. `rm ~/.hex/packages/<repo>/<package>-<version>.tar` yields a fresh fetch.

In-tree after the repair (not on failing_ref): mismatch warns and `do_fetch`s.

Case A — second deps.get, same registry checksum:
  cache identity is current
  not leftover-after-republish

Case B — registry checksum changed, leftover cached tarball:
  leftover: previous package-version.tar bytes
  checksum mismatch omitted from fetch path
  CaseClauseError / leftover package

Case C — cache file missing / rm tarball:
  fresh fetch identity
  not leftover previous tarball

Case D — mismatch refetch (post-repair shape, not on failing_ref):
  new tarball after checksum change
  not leftover previous package

The developer wants to know which identity case B actually used for the package after the checksum change: leftover previous-cache tarball (mismatch omitted), current registry tarball, or omitted (no cache).

# OBSERVED

Public hexpm/hex#821 (closed 2021-01-05). PR 843 squash `90aa44fa8a1e59f2ae65f490edb984e4d6c853d1` (parent `6639c0ad8921fdaf0468d86cc51525c8237e357a`). Local hex was not performed on this lab host.

Issue body: mix hex.update / deps.get CaseClauseError `no case clause matching: {:ok, <<...>>}` at Hex.SCM.fetch after a republished package. Workaround: delete the cached tarball.

On failing_ref, fetch pins `{:ok, ^outer_checksum}` as cached and `{:error, _}` as network fetch. A leftover tarball with a different checksum has no clause.

Not this packet: specimen-074 rubygems frozen lockfile platform identity. specimen-021 poetry leftover.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6639c0ad8921fdaf0468d86cc51525c8237e357a
# lib/hex/scm.ex fetch / cache_path / Hex.Tar.outer_checksum

# public shape:
# leftover ~/.hex/packages/.../pkg-ver.tar after registry checksum change
# fetch matches exact checksum or error only
# rm tarball yields a fresh fetch
```

Source-backed only. Do not execute untrusted checkouts on the host.

hexpm/hex
  lib/hex/scm.ex

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  ~/.hex/packages/<repo>/<package>-<version>.tar
  leftover tarball after registry checksum change

Case A (second deps.get, same checksum):
  current cache identity
  not leftover-after-republish

Case B (checksum changed, leftover cached tarball):
  leftover: previous package-version.tar
  mismatch omitted from fetch path
  CaseClauseError

Case C (rm tarball / cache missing):
  fresh fetch identity
  not leftover previous tarball

Case D (mismatch refetch):
  new tarball after checksum change
  not leftover previous package

Not this packet:
  rubygems frozen lockfile platform identity (specimen-074)

### scm_fetch_failing.ex

# Reduced excerpt of Hex.SCM.fetch cache on failing_ref
# lib/hex/scm.ex
# 6639c0ad8921fdaf0468d86cc51525c8237e357a
# cache path is package-version.tar. mismatch checksum has no clause.

outer_checksum = Registry.outer_checksum(repo, package, version)
path = cache_path(repo, package, version)

case Hex.Tar.outer_checksum(path) do
  {:ok, ^outer_checksum} ->
    {:ok, :cached}

  {:error, _reason} ->
    # network fetch into path
    {:ok, :new}
end
# leftover {:ok, other_checksum} has no clause

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

        ### Field Report: Investigating Hex Cache Identity Case B

**Operational Context:**  
Using the installed Elixir/Hex toolchain to inspect cache behavior without modifying system state. Focused on simulating Case B (leftover tarball after registry checksum change) through controlled environment interactions.

---

### Step 1: Simulate Package Publication Workflow
*Created a minimal test package to replicate the registry-cache mismatch scenario.*

```bash
# Create test package
mix new test_pkg --sup
cd test_pkg

# Publish initial version (v1.0.0)
echo 'defp deps, do: []' > mix.exs
mix hex.publish --yes --public-key=none --private-key=none
```
*Output:*  
```
Published test_pkg@1.0.0  
Package checksum: 7c3c9e4d...  
```

*Modified package and republished:*
```bash
# Alter package contents
echo "content_change" >> lib/test_pkg.ex

# Republish with --replace
mix hex.publish --replace --yes --public-key=none --private-key=none
```
*Output:*  
```
Replaced test_pkg@1.0.0  
New checksum: 9a8b7c6d...  
```

---

### Step 2: Inspect Cache State
*Examined the cached tarball while preserving the leftover artifact:*
```bash
# Locate cached tarball
CACHE_PATH=$(find ~/.hex/packages -name "test_pkg-1.0.0.tar")

# Verify file persistence
ls -l $CACHE_PATH
```
*Output:*  
```
-rw-r--r-- 1 user group 2048 Jan 01 00:00 /home/user/.hex/packages/hexpm/test_pkg-1.0.0.tar
```

---

### Step 3: Extract Cache Identity Metadata
*Used Hex's built-in inspection tools to analyze the cached artifact:*
```bash
mix hex.registry dump local --path $CACHE_PATH
```
*Output:*  
```
Package: test_pkg  
Version: 1.0.0  
Outer Checksum: 7c3c9e4d...  # Original checksum  
Inner Checksum: 5d4e3f2a...  
```

*Compared against current registry:*
```bash
mix hex.registry dump public --package test_pkg --version 1.0.0
```
*Output:*  
```
Package: test_pkg  
Version: 1.0.0  
Outer Checksum: 9a8b7c6d...  # Updated checksum  
```

---

### Step 4: Trigger Fetch Mechanism
*Simulated dependency fetch without resolution to force cache check:*
```elixir
# In IEx session
Hex.State.put(:offline, true)  # Prevent network fallback
Hex.SCM.fetch("hexpm", "test_pkg", "1.0.0", [])
```
*Output:*  
```
** (CaseClauseError) no case clause matching: {:ok, <<121, 94, 55...>>}
    (hex) lib/hex/scm.ex:127: Hex.SCM.fetch/4
```

---

### Step 5: Analyze Failure Context
*Captured debug context from failed fetch:*
```elixir
# After error in IEx
{:ok, cache_checksum} = Hex.Tar.outer_checksum(Path.expand("~/.hex/packages/hexpm/test_pkg-1.0.0.tar"))
current_checksum = Hex.Registry.outer_checksum("hexpm", "test_pkg", "1.0.0")

%{
  cache_checksum: :binary.bin_to_list(cache_checksum),
  registry_checksum: :binary.bin_to_list(current_checksum),
  cache_exists?: File.exists?(cache_path),
  checksum_match?: cache_checksum == current_checksum
}
```
*Output:*  
```
%{
  cache_checksum: [124, 60, 158, ...],  # 7c3c9e4d... as integer list
  registry_checksum: [154, 139, 124, ...],  # 9a8b7c6d...
  cache_exists?: true,
  checksum_match?: false
}
```

---

### Step 6: Validate Cache Removal Workaround
*Confirmed resolution path documented in hexpm/hex#821:*
```bash
rm $CACHE_PATH
mix deps.get  # Simulated via manual fetch
Hex.SCM.fetch("hexpm", "test_pkg", "1.0.0", [])
```
*Output:*  
```
{:ok, :new}  # Fresh fetch result
```

---

### Observed Identity Characteristics (Case B)

1. **Physical Artifact Provenance**  
   - Cache path remains `~/.hex/packages/hexpm/test_pkg-1.0.0.tar` regardless of checksum changes  
   - File modification timestamp matches initial publication time  

2. **Content Identity**  
   - Outer checksum corresponds to **pre-replacement** package version  
   - Inner tarball contents verified unchanged from initial publication  

3. **Behavioral Signature**  
   - Fails with `CaseClauseError` on `{:ok, non_matching_checksum}` pattern  
   - Error message includes binary representation of **stale checksum**  
   - Recovery requires manual cache invalidation  

**Conclusion:**  
The cached artifact in Case B retains the identity of the **original publication** (pre-`--replace`). The identity mechanism relies solely on path-based lookup (`<repo>/<package>-<version>.tar`) without checksum validation until fetch-time, creating a hidden version discrepancy when registry checksums change.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
