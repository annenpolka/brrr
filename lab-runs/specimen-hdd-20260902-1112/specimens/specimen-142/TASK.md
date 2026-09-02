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
