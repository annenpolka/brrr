repository: ansible-collections/community.general
issue: https://github.com/ansible-collections/community.general/issues/9710
pr: https://github.com/ansible-collections/community.general/pull/9760
failing_ref (parent of squash on main): 94e1511005e621f56002f3b057d03b46f7639fb3
fixed_ref (refresh persists _results as cache file): d696bb7b8992bfc6535c5e51dd37a00b9b4e22df
merged_at: 2025-02-17T17:45:31Z
pr_author: iqt4
merged_by: felixfontein
changed_files: plugins/inventory/proxmox.py, changelogs/fragments/9760-proxmox-inventory.yml
pr_title: proxmox inventory: proposal for #9710 (caching)
scout_note: not 136 pants process cache. leftover inventory jsonfile keyed by inventory file path after world change. unique vs 001-141.
