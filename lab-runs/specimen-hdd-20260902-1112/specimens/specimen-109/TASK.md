# TASK

`mise upgrade` of **one tracked project** can drop the install identity still named by **another tracked project's lockfile**.

Two sibling dirs, both `dummy = "latest"`, both `mise.lock` pin `1.0.0`:

```
tracked-upgrade/foo/{mise.toml,mise.lock}   dummy @ 1.0.0
tracked-upgrade/bar/{mise.toml,mise.lock}   dummy @ 1.0.0
```

On failing_ref `2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c`, after `cd bar && mise upgrade dummy@2.0.0`, cleanup calls `get_versions_needed_by_tracked_configs(config, false, false)` — `use_locked_version=false` for **every** tracked config. Foo's lock still names `1.0.0`. The keep-set does not. `1.0.0` is uninstalled. Foo's lock identity is leftover against a missing install.

In-tree after the repair (not on failing_ref): `e2e/cli/test_upgrade` block "upgrading one tracked project should preserve versions pinned by another tracked lockfile". After bar upgrades to `2.0.0`: `mise ls --installed dummy` still contains `1.0.0` and `2.0.0`; foo's lock stays `1.0.0`; bar's lock is `2.0.0` and not `1.0.0`.

Case A — single tracked project, upgrade dummy 1.0.0 → 2.0.0:
  old 1.0.0 is this project's stale lock
  uninstall of 1.0.0 is intended
  no leftover sibling pin

Case B — two tracked projects, both locked 1.0.0; upgrade only bar to 2.0.0:
  failing_ref keep-set ignores foo's lock
  leftover identity: foo lock pin 1.0.0 vs missing install
  bar lock 2.0.0 vs installed 2.0.0 stay joined

Case C — `mise prune` (not upgrade) with lockfiles enabled:
  prune already passed `use_locked_version=true`
  not this upgrade leftover

Case D — two projects share the same lockfile path:
  one pin, not sibling leftover

The developer wants to know which identity case B actually kept after bar's upgrade: leftover missing install for foo's still-pinned 1.0.0, both pins installed, or omitted foo lock.
