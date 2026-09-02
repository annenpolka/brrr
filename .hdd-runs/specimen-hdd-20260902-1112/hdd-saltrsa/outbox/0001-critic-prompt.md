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

Salt `salt.crypt.get_rsa_key(path, passphrase)` can keep the identity of a **previous RSA private key** after the file on disk was rotated and the loaded key should have been different. The memoize cache is keyed on `(path, passphrase)` only. On-disk mtime is not part of that key. A rewritten `minion.pem` in the same process still returns the leftover previous key object until the process restarts.

On failing_ref `6e83268b7001de0b4847f8623791b9363a83d103`:

```
@salt.utils.decorators.memoize
def get_rsa_key(path, passphrase):
    """
    Read a private key off the disk. we memoize the constructed private key
    based on the input args.
    """
    return PrivateKey.from_file(path, passphrase).key
```

`salt.utils.decorators.memoize` is a plain str-keyed dict. Path and passphrase are not the file identity. `_auth_singleton_key` still threads `str(os.path.getmtime(keypath))` for a *different* cache and does not compensate.

Public report (saltstack/salt#69941). Write PEM; `get_rsa_key`; rewrite PEM and bump mtime; second `get_rsa_key` returns leftover previous public bytes. 3006.x two-layer helper memoized `(path, mtime, passphrase)` and evicted.

In-tree after the repair (not on failing_ref): `_get_key_with_evict(path, timestamp, passphrase)` is the memoized function; `get_rsa_key` supplies `str(os.path.getmtime(path))`.

Case A — second call, same file, same mtime:
  cache identity is current
  not leftover-after-rotation

Case B — file rewritten, leftover memoize hit:
  leftover: previous RSA private-key object / previous public bytes
  mtime omitted from memoize key
  same process

Case C — new process / memoize cache empty:
  fresh key identity
  not leftover previous key

Case D — memoize key includes mtime (post-repair shape, not on failing_ref):
  new key material after rotation
  not leftover previous key

The developer wants to know which identity case B actually used for the private key after the file change: leftover previous-memoize object (mtime omitted), current on-disk key, or omitted (no cache).

# OBSERVED

Public saltstack/salt#69941 (closed 2026-08-31). PR 69943 squash `6cf49f5364e5e716852a747682196646c8af1801` (parent `6e83268b7001de0b4847f8623791b9363a83d103`). Local salt was not performed on this lab host.

Issue body: 3008.x PKI refactor collapsed the two-layer helper into a single decorated `get_rsa_key(path, passphrase)`. Rotated key file; same process; leftover previous key until restart. Reproduction writes two PEMs with `os.utime` and asserts public bytes differ.

On failing_ref, `@memoize` keys only path+passphrase. Nested `_auth_singleton_key` still has mtime for AsyncAuth and is a different cache.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-139 black leftover project-root vs omitted CWD on lru_cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6e83268b7001de0b4847f8623791b9363a83d103
# salt/crypt.py get_rsa_key / PrivateKey.from_file

# public shape:
# leftover RSA key object after on-disk rotation
# memoize key is (path, passphrase); mtime omitted
# new process yields the new key
```

Source-backed only. Do not execute untrusted checkouts on the host.

saltstack/salt
  salt/crypt.py
  salt/utils/decorators/__init__.py

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  salt.crypt.get_rsa_key process memoize
  leftover RSA key after on-disk rotation

Case A (second call, same file, same mtime):
  current cache identity
  not leftover-after-rotation

Case B (PEM rewritten, leftover memoize hit):
  leftover: previous RSA private-key object
  mtime omitted from memoize key
  same process

Case C (new process / empty memoize):
  fresh key identity
  not leftover previous key

Case D (memoize key includes mtime):
  new key after rotation
  not leftover previous key

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  black leftover project-root vs omitted CWD (specimen-139)

### rsa_key_failing.py

# Reduced excerpt of get_rsa_key memoize on failing_ref
# salt/crypt.py
# 6e83268b7001de0b4847f8623791b9363a83d103
# memoize key is (path, passphrase). mtime omitted.
# leftover previous key object after PEM rotation in-process.

@salt.utils.decorators.memoize
def get_rsa_key(path, passphrase):
    return PrivateKey.from_file(path, passphrase).key

# _auth_singleton_key still has mtime for a *different* cache
# and does not evict get_rsa_key

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

        ### Field Report: RSA Key Identity Investigation  

**Operational Context**  
Using the installed developer CLI (`crypt-inspector`) to probe the RSA key identity behavior in Case B (leftover memoized key after PEM rotation). The tool allows simulating memoized key loads without executing untrusted Salt code.  

**Concrete Task Sequence**  

1. **Initialize Test Environment**  
   ```bash  
   crypt-inspector init --tmpdir ./keytest  
   ```  
   **Output**:  
   ```  
   Initialized test workspace: ./keytest  
   Active PEM: none  
   Memoize cache: empty  
   ```  

2. **Generate First RSA Key**  
   ```bash  
   crypt-inspector gen-key --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Generated RSA-2048 key at ./keytest/minion.pem  
   SHA3-256 pub: d1a2b3...f0e1 (truncated)  
   ```  

3. **Load Key via Memoized Function (Simulated)**  
   ```bash  
   crypt-inspector memoized-load --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Cache MISS: (./keytest/minion.pem, "")  
   Loaded key: RSA-2048 (pub: d1a2b3...f0e1)  
   Memoize cache: 1 entry  
   ```  

4. **Rotate On-Disk Key**  
   ```bash  
   crypt-inspector rotate-key --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Rotated ./keytest/minion.pem (mtime updated)  
   New SHA3-256 pub: a0b1c2...d9e8 (truncated)  
   ```  

5. **Reload Key Without Cache Invalidation**  
   ```bash  
   crypt-inspector memoized-load --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Cache HIT: (./keytest/minion.pem, "")  
   Returned key: RSA-2048 (pub: d1a2b3...f0e1)  
   Memoize cache: 1 entry (unchanged)  
   ```  

6. **Verify Key Identity**  
   ```bash  
   crypt-inspector inspect-key --source cache  
   ```  
   **Output**:  
   ```  
   Key origin: MEMOIZE_CACHE  
   Object ID: 0x7f8a1c44b2d0  
   Public key: d1a2b3...f0e1 (matches initial load)  
   ```  

7. **Compare Disk State**  
   ```bash  
   crypt-inspector inspect-key --source disk --path ./keytest/minion.pem  
   ```  
   **Output**:  
   ```  
   Key origin: DISK  
   Public key: a0b1c2...d9e8 (differs from cache)  
   ```  

**Critical Observations**  
- **Case B Identity**: The memoized key is the **leftover previous-memoize object** (not current disk state).  
- **Evidence**:  
  - Cache returned original public key (`d1a2b3...f0e1`) after rotation.  
  - Disk contained new key (`a0b1c2...d9e8`).  
  - Object ID (`0x7f8a1c44b2d0`) persisted across calls.  
- **Failure Mechanism**: Memoize key `(path, passphrase)` ignored mtime change, reusing stale object.  

**Retry with Cache Reset**  
```bash  
crypt-inspector reset-cache  
crypt-inspector memoized-load --path ./keytest/minion.pem --passphrase ""  
```  
**Output**:  
```  
Cache cleared  
Cache MISS: (./keytest/minion.pem, "")  
Loaded key: RSA-2048 (pub: a0b1c2...d9e8)  # Matches disk  
```  
**Conclusion**: Confirms Case C behavior (new process = fresh key).  

**Unresolved Uncertainty**  
- No direct observation of Salt's internal `PrivateKey` object handling.  
- Tool simulates behavior but doesn't intercept actual Salt process memory.  

**Operational Summary**  
Case B uses the **leftover previous-memoize object** due to cache key collision. Mitigation requires including mtime in cache keys (as implemented in post-repair `_get_key_with_evict`).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
