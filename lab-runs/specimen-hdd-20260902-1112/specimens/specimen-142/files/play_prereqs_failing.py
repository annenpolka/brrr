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
