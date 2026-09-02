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

Ansible `--flush-cache` can keep the identity of a **previous inventory cache** after a refresh should have been a miss. `_play_prereqs` constructs `InventoryManager` without a cache flag, so `__init__` always `parse_sources(cache=True)`. `_flush_cache` only `clear_facts` per host. Inventory is omitted from the flush.

On failing_ref `c9db73f04e7a5fae7bbbdff8efbd585d15971d31`:

```
inventory = InventoryManager(loader=loader, sources=options['inventory'])
# InventoryManager.__init__:
if parse:
    self.parse_sources(cache=True)

# PlaybookCLI after prereqs:
if context.CLIARGS['flush_cache']:
    self._flush_cache(inventory, variable_manager)
# _flush_cache: variable_manager.clear_facts(hostname) only
```

Public report (ansible/ansible#73699). Dummy inventory plugin; `--flush-cache` still prints "Using data from cache".

In-tree after the repair (not on failing_ref): `InventoryManager(..., cache=(not options.get('flush_cache')))` so parse_sources gets cache=False on flush.

Case A — second playbook without --flush-cache, unchanged inventory:
  cache identity is current
  not leftover-after-flush

Case B — --flush-cache, leftover inventory plugin cache:
  leftover: previous inventory parse
  inventory omitted from flush (facts only)
  plugin still sees cache=True

Case C — delete inventory jsonfile cache dir then run:
  fresh inventory identity
  not leftover previous parse

Case D — InventoryManager cache=False on flush (post-repair shape, not on failing_ref):
  cache miss / "Updating cache"
  not leftover previous inventory

The developer wants to know which identity case B actually used for inventory after --flush-cache: leftover previous-inventory results (flush omitted inventory), current inventory identity, or omitted (no cache).

# OBSERVED

Public ansible/ansible#73699 (closed 2022-03-17). PR 77083 merge `94b73d66d53ca0df9911d1dd412bc1d3c9181b1b` (parent `c9db73f04e7a5fae7bbbdff8efbd585d15971d31`). Local ansible was not performed on this lab host.

Issue body: --flush-cache still passes cache=True into inventory plugins; docs say refresh should update cache. _flush_cache only clears facts.

On failing_ref, InventoryManager always parse_sources(cache=True). PR 77083 threads cache=(not flush_cache) into InventoryManager.

Not this packet: specimen-136 pants leftover process cache vs git hash. ansible#38394 leftover vars_files closed without PR.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c9db73f04e7a5fae7bbbdff8efbd585d15971d31
# lib/ansible/cli/__init__.py _play_prereqs
# lib/ansible/inventory/manager.py parse_sources(cache=True)
# lib/ansible/cli/playbook.py _flush_cache facts only

# public shape:
# leftover inventory cache after --flush-cache
# inventory omitted from flush; facts-only
```

Source-backed only. Do not execute untrusted checkouts on the host.

ansible/ansible
  lib/ansible/cli/__init__.py
  lib/ansible/cli/playbook.py
  lib/ansible/inventory/manager.py

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  inventory cache plugin jsonfile
  leftover inventory after --flush-cache

Case A (second playbook, no --flush-cache):
  current cache identity
  not leftover-after-flush

Case B (--flush-cache, leftover inventory plugin cache):
  leftover: previous inventory parse
  inventory omitted from flush (facts only)
  plugin still sees cache=True

Case C (delete jsonfile cache dir):
  fresh inventory identity
  not leftover previous parse

Case D (InventoryManager cache=False on flush):
  cache miss / Updating cache
  not leftover previous inventory

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  ansible leftover vars_files (#38394 closed without PR)

### play_prereqs_failing.py

# Reduced excerpt of CLI._play_prereqs / InventoryManager on failing_ref
# lib/ansible/cli/__init__.py + inventory/manager.py
# c9db73f04e7a5fae7bbbdff8efbd585d15971d31
# Inventory always parsed with cache=True. --flush-cache omitted.

inventory = InventoryManager(loader=loader, sources=options['inventory'])
# InventoryManager.__init__:
#   if parse:
#       self.parse_sources(cache=True)

# PlaybookCLI:
# if context.CLIARGS['flush_cache']:
#     self._flush_cache(inventory, variable_manager)
# _flush_cache: variable_manager.clear_facts(hostname) only
# FIXME: flush inventory cache  (comment in clear_caches)

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

        ### Field Report: Investigating Ansible Inventory Cache Identity with `--flush-cache`

**Environment Setup**:  
- Active Ansible installation exhibiting behavior from failing_ref `c9db73f04e7a5fae7bbbdff8efbd585d15971d31`  
- JSON file cache plugin enabled  
- Custom test inventory plugin (`test_plugin.py`) created to log cache usage  
- Cache directory: `./cache_dir`  
- Inventory source: `inventory.test`  

---

#### **Step 1: Initialize Cache with First Playbook Run**
```bash
$ echo "host1" > inventory.test
$ ansible-playbook -i inventory.test test.yml
```
**Output**:  
```
PLAY [all] *********************************************************************
TASK [debug] *******************************************************************
ok: [host1] => {"inventory_hostname": "host1"}
```

**Cache State Post-Run**:  
```bash
$ ls cache_dir/
ansible-inventory.cache
$ cat cache_dir/ansible-inventory.cache
{"_data": {"test_plugin_cache_key": {"hosts": ["host1"]}}, ...}
```
**Observation**:  
- Inventory cache created with `host1` identity  
- Test plugin saved state to cache  

---

#### **Step 2: Modify Inventory Source**
```bash
$ echo "host2" > inventory.test  # Change inventory content
```

---

#### **Step 3: Run with `--flush-cache` (Case B)**
```bash
$ ansible-playbook -i inventory.test test.yml --flush-cache -v
```
**Output**:  
```
TASK [debug] *******************************************************************
test_plugin: USING CACHED DATA. KEY: test_plugin_cache_key
ok: [host1] => {"inventory_hostname": "host1"}
```
**Critical Observations**:  
1. Plugin log confirms `USING CACHED DATA`  
2. Output shows `host1` (old inventory) despite source now containing `host2`  
3. No "Updating cache" message observed  

**Cache State Post-Run**:  
```bash
$ cat cache_dir/ansible-inventory.cache
{"_data": {"test_plugin_cache_key": {"hosts": ["host1"]}}, ...}  # Unchanged
```

---

#### **Step 4: Contrast with No-Flush Scenario (Case A)**
```bash
$ ansible-playbook -i inventory.test test.yml  # No flush
```
**Output**:  
```
TASK [debug] *******************************************************************
test_plugin: USING CACHED DATA. KEY: test_plugin_cache_key
ok: [host1] => {"inventory_hostname": "host1"}  # Still host1 (cache valid)
```
**Observation**:  
- Expected cache reuse when inventory unchanged  

---

#### **Step 5: Fresh Cache Scenario (Case C)**
```bash
$ rm -rf cache_dir/*  # Delete cache
$ ansible-playbook -i inventory.test test.yml
```
**Output**:  
```
test_plugin: CACHE MISS. PARSING: inventory.test
PLAY [all] *********************************************************************
TASK [debug] *******************************************************************
ok: [host2] => {"inventory_hostname": "host2"}  # New identity
```
**Observation**:  
- Cache miss forces fresh parse  
- Correct `host2` inventory loaded  

---

#### **Step 6: Verify Plugin Cache Logic**
Inspected test plugin behavior during runs:  
```python
# test_plugin.py (excerpt)
if cache and self._cache.get(cache_key):
    print(f"test_plugin: USING CACHED DATA. KEY: {cache_key}")  # Seen in Case B
else:
    print(f"test_plugin: CACHE MISS. PARSING: {path}")  # Seen in Case C
```

---

### Conclusions from Observed Behavior  

1. **Case B Identity**:  
   - Inventory retained **leftover previous identity** (`host1`)  
   - `--flush-cache` did not invalidate inventory cache  
   - Cache flag remained `True` in plugin context  

2. **Failure Mechanism**:  
   - `_flush_cache` only cleared facts (per issue)  
   - `parse_sources(cache=True)` reused stale cache  
   - Cache plugin returned pre-flush data  

3. **Negative Controls Validated**:  
   - Case C (cache deletion) showed fresh identity  
   - Case A (no flush) showed expected cache reuse  

4. **No Cache Update Attempt**:  
   - Plugin never reached cache-write logic during flush run  
   - Cache key unchanged between runs  

**Final Status**:  
➜ **Case B uses leftover previous-inventory cache identity**  
➜ Cache omission confirmed via plugin logs and output behavior

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
