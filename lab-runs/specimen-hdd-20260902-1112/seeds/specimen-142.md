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
