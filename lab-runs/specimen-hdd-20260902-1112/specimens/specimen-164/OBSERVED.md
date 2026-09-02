# OBSERVED

Public fxn/zeitwerk commit `f9b21aa3dbeef14be794ccf534f1a21cb2e004a1` (parent `8100bd18a42c29740e2d30d21b5f68be67f27d1b`). Changelog 2.6.18 (2 September 2024). Test `reloading namespaces that are inceptions in other projects`. Local zeitwerk was not performed on this lab host.

Commit title: Fix autoload_path_set_by_me_for? with inceptions. Files: `lib/zeitwerk/loader.rb`, `lib/zeitwerk/registry.rb`, `test/lib/zeitwerk/test_reloading.rb`.

On failing_ref, `Registry.inception?(cpath)` returns the path for any loader. Gem `for_gem` inception of `MyGem` is leftover helper identity for the app loader. Reload does not restore app-added `MyGem::Foo`.

Not this packet: specimen-054 cpython generated-code drift. specimen-110 composer leftover abandoned. specimen-157 jest haste leftover mock name (leftover-flag). specimen-159 gleam leftover compile cache after move+restore (leftover-flag). specimen-160 crystal omitted target_def_ids. specimen-163 kotlin omitted dep fingerprint.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
