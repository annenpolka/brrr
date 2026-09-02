repository: ansible/ansible
issue: https://github.com/ansible/ansible/issues/73699
pr: https://github.com/ansible/ansible/pull/77083
failing_ref (parent of merge on devel): c9db73f04e7a5fae7bbbdff8efbd585d15971d31
fixed_ref (InventoryManager cache=not flush_cache): 94b73d66d53ca0df9911d1dd412bc1d3c9181b1b
merged_at: 2022-03-17T18:15:03Z
pr_author: bcoca
merged_by: bcoca
changed_files: lib/ansible/cli/__init__.py, lib/ansible/inventory/manager.py, changelog
pr_title: inventory manager respect --flush-cache
scout_note: not 136 pants process cache. Distinct leftover: --flush-cache omitted inventory so leftover plugin cache stayed current. unique vs 001-141.
