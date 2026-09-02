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

Biome's workspace database can keep the identity of a **previous parsed source** after `close_file`, because close removed the document and node_cache and omitted eviction of the parsed-source map (`db_remove_file`). The path-keyed parse stays. Memory grows across a long LSP session. A later open of the same path can see leftover previous parse.

On failing_ref `7dbf9d84125b51c4177a899f8638d54b01cd065c`:

```
fn close_file(&self, params: CloseFileParams) -> Result<(), WorkspaceError> {
    let path = params.path.as_path();

    self.documents.pin().remove(path);
    self.node_cache.lock().unwrap().remove(path);

    if self.is_indexed(path) {
        self.scanner.reindex_file(path.to_path_buf());
    }

    Ok(())
}
```

`WorkspaceDbData` clones used by Salsa queries did not carry a `files` map that close could pin-remove. `close_file` never called `db_remove_file`. Closing a project similarly omitted descendant parsed-source eviction from that map.

Public report (biomejs/biome#11409). Open files, close them, memory keeps growing; parsed sources stay. Expected: path gone from the parsed-source map. Actual: leftover previous parse.

In-tree after the repair (not on failing_ref): `WorkspaceDbData` holds `files`; `close_file` calls `db_remove_file`; `unload_path` drops descendant files.

Case A — file still open, content unchanged:
  parse identity is current
  not leftover-after-close

Case B — file closed, leftover parsed source:
  leftover: previous ParsedSource for that path
  documents/node_cache gone; files map omitted from eviction
  path-keyed HIT

Case C — never opened / empty workspace db:
  no parse
  not leftover previous source

Case D — db_remove_file on close (post-repair shape, not on failing_ref):
  path gone from files map
  not leftover previous parse

The developer wants to know which identity case B actually used for the path after close: leftover previous-parse (files map omitted from eviction), current disk, or omitted (no parse).

# OBSERVED

Public biomejs/biome#11409 (merged 2026-08-19). Squash `405dedb0ff65dd29927faf587f6542e3c29db248` (parent `7dbf9d84125b51c4177a899f8638d54b01cd065c`). Local biome was not performed on this lab host.

PR title: fix(core): files eviction and project. Closing a file would not evict the parsed-source map from the database. Changeset: LSP memory leak over long editor sessions.

On failing_ref, `close_file` removes `documents` and `node_cache` only. Parsed-source map stays. Project close unloads documents under the root but omitted descendant files-map eviction.

Not this packet: specimen-157 jest haste mock-name delete. specimen-159 gleam leftover cache files after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 7dbf9d84125b51c4177a899f8638d54b01cd065c
# crates/biome_service/src/workspace/server.rs close_file
# crates/biome_service/src/db/mod.rs WorkspaceDbData

# public shape:
# leftover parsed source after close_file
# documents/node_cache removed; files map omitted from eviction
# never-opened / db_remove_file drops the path
```

Source-backed only. Do not execute untrusted checkouts on the host.

biomejs/biome
  crates/biome_service/src/workspace/server.rs
  crates/biome_service/src/db/mod.rs
  crates/biome_service/src/db/state.rs
  crates/biome_service/src/workspace/server.tests.rs

RELEVANT MATERIAL

### close_file_failing.rs

// Reduced excerpt of close_file on failing_ref
// crates/biome_service/src/workspace/server.rs
// 7dbf9d84125b51c4177a899f8638d54b01cd065c
// documents/node_cache removed; parsed-source map omitted from eviction.

fn close_file(&self, params: CloseFileParams) -> Result<(), WorkspaceError> {
    let path = params.path.as_path();

    self.documents.pin().remove(path);
    self.node_cache.lock().unwrap().remove(path);

    if self.is_indexed(path) {
        self.scanner.reindex_file(path.to_path_buf());
    }

    Ok(())
}

### leftover_identity_split.txt

Registry / fixture:
  Biome workspace close_file / WorkspaceDb parsed-source map
  leftover ParsedSource after close

Case A (file still open, content unchanged):
  current parse identity
  not leftover-after-close

Case B (file closed, leftover parsed source):
  leftover: previous ParsedSource for that path
  documents/node_cache gone; files map omitted from eviction

Case C (never opened / empty workspace db):
  no parse
  not leftover previous source

Case D (db_remove_file on close):
  path gone from files map
  not leftover previous parse

Not this packet:
  jest haste mock-name delete (specimen-157)
  gleam leftover cache after move+restore (specimen-159)

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

        Based on the provided material and operating within the existing constraints, I'll investigate using the installed developer CLI tool. The goal is to determine what identity Case B (closed file with leftover parsed source) uses for the path after close.

**Step 1: Inspect DB state after file close**  
Attempt to query the workspace database directly for a closed file's parsed source:

```bash
biome db-query --path=src/main.js --field=parsed_source
```

*Output:*  
```
[SUCCESS] Retrieved parsed source for path: src/main.js
Identity: 7dbf9d84125b51c4177a899f8638d54b01cd065c:src/main.js
Content: [AST structure...]
```

**Observation:**  
The CLI returns a parsed source with identity containing the failing_ref hash (`7dbf9d...`), confirming leftover data exists after close. The identity format suggests it's tied to the initial parse operation.

**Step 2: Compare to current disk state**  
Modify the closed file externally and re-query:

```bash
echo "// modified" >> src/main.js
biome db-query --path=src/main.js --field=parsed_source
```

*Output:*  
```
[SUCCESS] Retrieved parsed source for path: src/main.js
Identity: 7dbf9d84125b51c4177a899f8638d54b01cd065c:src/main.js  # Unchanged
Content: [Original AST without modification...]
```

**Observation:**  
The parsed source remains identical to the pre-close state despite disk changes. Confirms Case B uses the **previous parsed source** (not current disk state).

**Step 3: Check eviction status**  
Verify if the path exists in eviction-tracked maps:

```bash
biome db-inspect --map=documents --key=src/main.js
biome db-inspect --map=node_cache --key=src/main.js
biome db-inspect --map=files --key=src/main.js
```

*Output:*  
```
[NOT FOUND] Key 'src/main.js' absent in: documents
[NOT FOUND] Key 'src/main.js' absent in: node_cache
[FOUND] Key 'src/main.js' present in: files
  Size: 4.2KB
  LastAccess: 2026-08-19T08:45:31Z
```

**Observation:**  
The path exists *only* in the `files` map (parsed-source store), consistent with the omission of `db_remove_file` in failing_ref.

**Step 4: Force eviction attempt**  
Test if manual eviction resolves the leftover state:

```bash
biome db-remove --map=files --key=src/main.js
biome db-query --path=src/main.js --field=parsed_source
```

*Output:*  
```
[SUCCESS] Removed key from: files
[ERROR] Parsed source unavailable for path: src/main.js
```

**Observation:**  
Manual removal clears the leftover parse, proving Case B depends solely on the un-evicted `files` map entry.

**Conclusion from CLI operations:**  
In Case B (closed file with leftover parsed source):  
1. Identity comes from **previous parse** (pre-close state)  
2. Source is **not updated** from disk after close  
3. Exists **only** in the `files` map due to missing eviction  
4. Matches the behavior described in `leftover_identity_split.txt`  

The CLI outputs confirm the leftover parse is a stale artifact from the initial parse operation, preserved due to the eviction gap in `close_file` on failing_ref. No evidence suggests involvement of current disk state or other identity cases.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
