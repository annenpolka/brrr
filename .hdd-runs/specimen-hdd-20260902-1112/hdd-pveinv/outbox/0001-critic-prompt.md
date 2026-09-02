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

Ansible `community.general.proxmox` inventory with `cache: true` can keep the identity of a **previous inventory JSON** after the Proxmox world changed (new LXC) and `meta: refresh_inventory` should have been a different host set. The cache key is inventory **file** identity (`get_cache_key(path)`). The plugin has only `use_cache = cache and get_option('cache')`. On refresh, `cache=False` so it refetches in memory, but it does not persist a new cache file. The next playbook run hits leftover previous hosts.

On failing_ref `94e1511005e621f56002f3b057d03b46f7639fb3`:

```
self.cache_key = self.get_cache_key(path)
self.use_cache = cache and self.get_option('cache')
# _get_json:
if not self.use_cache or url not in self._cache.get(self.cache_key, {}):
    ...
    self._cache[self.cache_key][url] = data
return make_unsafe(self._cache[self.cache_key][url])
self._populate()
```

`get_cache_key(path)` is the inventory yaml path, not the remote host set. Nested writes into an existing `_cache[self.cache_key]` dict do not replace the cache file after refresh.

Public report (ansible-collections/community.general#9710). Create LXC; `meta: refresh_inventory`; in-memory inventory has the new host; cache file timestamp/content unchanged; second run without handler uses leftover previous inventory until the cache dir is deleted.

In-tree after the repair (not on failing_ref): `update_cache = not cache and get_option('cache')`; results collected in `_results`; `self._cache[self.cache_key] = self._results` written in one go.

Case A — second inventory load, Proxmox unchanged, cache on:
  cache identity is current
  not leftover-after-world-change

Case B — new LXC then leftover cache file (refresh did not persist):
  leftover: previous proxmox inventory JSON / missing new hostname
  cache keyed by inventory file path
  same `.cache` jsonfile

Case C — cache plugin off / cache dir deleted:
  fresh inventory identity
  not leftover previous hosts

Case D — refresh writes `_cache[cache_key] = results` (post-repair shape, not on failing_ref):
  cache miss / new host present on second run
  not leftover previous inventory

The developer wants to know which identity case B actually used for the inventory after the new LXC: leftover previous-file-keyed cache (refresh omitted persist), current Proxmox identity, or omitted (no cache).

# OBSERVED

Public ansible-collections/community.general#9710 (closed 2025-02-17). PR 9760 squash `d696bb7b8992bfc6535c5e51dd37a00b9b4e22df` (parent `94e1511005e621f56002f3b057d03b46f7639fb3`). Local ansible/proxmox was not performed on this lab host.

Issue body: proxmox inventory cache enabled; create LXC; `meta: refresh_inventory` updates in-memory inventory; cache file under `.cache` does not change; second play fails `hostvars['debian-t']` undefined until cache deleted.

On failing_ref, `_get_json` keys cache by inventory file path. Refresh sets `cache=False` so `use_cache` is false and the plugin refetches, but there is no separate persist path. Nested assignment into an existing cache dict leaves the previous jsonfile.

Not this packet: specimen-136 pants leftover process cache vs git hash. ansible-core#73699 leftover inventory vs `--flush-cache` (core manager, not proxmox file-keyed jsonfile).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 94e1511005e621f56002f3b057d03b46f7639fb3
# plugins/inventory/proxmox.py parse / _get_json / get_cache_key(path)

# public shape:
# leftover inventory cache file after meta:refresh_inventory
# cache keyed by inventory yaml path; new LXC omitted on second run
# until cache dir deleted
```

Source-backed only. Do not execute untrusted checkouts on the host.

ansible-collections/community.general
  plugins/inventory/proxmox.py

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  community.general.proxmox cache: true
  leftover inventory jsonfile after new LXC + refresh_inventory

Case A (second load, Proxmox unchanged):
  current cache identity
  not leftover-after-world-change

Case B (new LXC, leftover cache file):
  leftover: previous proxmox inventory JSON
  cache keyed by inventory file path
  new hostname omitted on second run

Case C (cache off / cache dir deleted):
  fresh inventory identity
  not leftover previous hosts

Case D (refresh writes _cache[key] = results):
  new host present on second run
  not leftover previous inventory

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  ansible-core leftover inventory vs --flush-cache (#73699)

### proxmox_cache_failing.py

# Reduced excerpt of proxmox inventory cache on failing_ref
# plugins/inventory/proxmox.py
# 94e1511005e621f56002f3b057d03b46f7639fb3
# cache_key is inventory file path. Nested write into existing dict.
# refresh (cache=False) refetches in memory; leftover jsonfile stays.

self.cache_key = self.get_cache_key(path)
self.use_cache = cache and self.get_option('cache')

def _get_json(self, url, ignore_errors=None):
    if not self.use_cache or url not in self._cache.get(self.cache_key, {}):
        if self.cache_key not in self._cache:
            self._cache[self.cache_key] = {'url': ''}
        data = []
        # ... HTTP GET into data ...
        self._cache[self.cache_key][url] = data
    return make_unsafe(self._cache[self.cache_key][url])

self._populate()

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

        ### Field Report: Investigating Proxmox Inventory Cache Identity  

**Tool Used**: `ansible-inspect` (unfamiliar CLI tool for analyzing Ansible plugin behavior without execution)  
**Operational Parameters**:  
- Source-only mode (no playbook execution)  
- Cache behavior simulation via static analysis  
- Input: `proxmox_cache_failing.py` excerpt + `leftover_identity_split.txt`  

---

#### Step 1: Establish Cache Key Identity  
```bash
ansible-inspect key-provenance --source proxmox_cache_failing.py --fixture leftover_identity_split.txt
```  
**Output**:  
```  
CACHE_KEY_SOURCE: inventory file path (via get_cache_key(path))  
CACHE_UPDATE_MECHANISM: nested dict assignment (_cache[cache_key][url])  
PERSISTENCE_TRIGGER: only when use_cache=True  
```  
**Observation**: Cache identity is bound to the inventory file path, not Proxmox state.  

---

#### Step 2: Simulate Refresh Workflow (Case B)  
```bash  
ansible-inspect simulate-refresh \  
  --cache-state initial.json \  
  --world-change "add_lxc: debian-t" \  
  --code proxmox_cache_failing.py  
```  
**Input**:  
- `initial.json`: Pre-refresh inventory (hosts: [node1, node2])  
- World change: New LXC `debian-t` added  

**Output**:  
```  
[REFRESH PHASE]  
use_cache: false (cache=False override)  
HTTP_FETCH: [node1, node2, debian-t]  # New host fetched  
MEMORY_CACHE_UPDATED: True  
DISK_CACHE_WRITTEN: False  # No self._cache[key]=full_results  
```  

**Failure**:  
```  
[SECOND RUN]  
use_cache: true (cache: true in config)  
CACHE_SOURCE: initial.json (disk)  
HOSTS_LOADED: [node1, node2]  # debian-t missing  
```  
**Observation**: Post-refresh disk cache remains identical to pre-refresh state.  

---

#### Step 3: Verify Cache Identity Provenance  
```bash  
ansible-inspect cache-identity \  
  --cache-file .cache/proxmox_cache.json \  
  --world-state post-refresh  
```  
**Output**:  
```  
CACHE_IDENTITY_SIGNATURE:  
  type: file_path_based  
  key: /etc/ansible/inventories/proxmox.yml  
  content_hash: 89a3b7e1 (matches initial.json)  
```  
**Conflict**:  
- In-memory state after refresh included `debian-t`  
- Disk cache signature unchanged since first run  

---

#### Step 4: Resolve Identity Conflict  
```bash  
ansible-inspect resolve-conflict \  
  --prior-observation "refresh updates memory" \  
  --new-fact "disk cache unchanged" \  
  --mechanism nested-dict-write  
```  
**Output**:  
```  
ROOT CAUSE: Partial cache update  
Nested dict assignment (_cache[key][url]) modifies existing cache dict  
but does not:  
  1. Invalidate the top-level cache key  
  2. Trigger persistence of the updated dict  
```  
**Retry with forced persistence**:  
```bash  
ansible-inspect patch-simulate \  
  --code proxmox_cache_failing.py \  
  --mod "add self._cache[key]=_cache[key] after _get_json"  
```  
**Result**:  
```  
DISK_CACHE_WRITTEN: True  
CACHE_SIGNATURE_CHANGED: True  
```  

---

### Verified Facts:  
1. **Case B Identity**: Leftover previous-file-keyed cache  
   - Cache key: Inventory file path (`/etc/ansible/inventories/proxmox.yml`)  
   - Content: Pre-refresh host list  
2. **Trigger**: `use_cache=False` during refresh prevents:  
   - Cache file invalidation  
   - Full-dict persistence (only nested URL data updated in-memory)  
3. **World-State Mismatch**:  
   - Proxmox state changed (new LXC)  
   - Cache identity remained bound to file path + old content  

### Conclusion:  
The failure occurs because the **cache identity is decoupled from Proxmox state changes**. The plugin:  
- Uses file-based identity (`get_cache_key(path)`)  
- Updates cache content partially during refresh  
- Fails to persist/associate the updated state with the identity  

**Recommendation from Within Environment**:  
> Implement cache-key regeneration when Proxmox state changes are detected (requires world-state fingerprinting). Until then, manual cache deletion remains necessary after dynamic resource changes.  

**Uncertainty**:  
- Actual persistence mechanism of Ansible's `CachePlugin` not visible in excerpt  
- No evidence of cache versioning or invalidation hooks  

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
