# OBSERVED

Public ruby/ruby PR 4715 (merged 2021-10-08). Commit `08759edea8fb75d46c3e75217e6613465426a0d2` (parent `ded5a66cb994c5731a17bc9a2420042248a2f1fe`). Bug #15790. Local ruby was not performed on this lab host.

PR title: Remove autoload for constant if the autoload fails. Test `test_autoload_after_failed_and_removed_from_loaded_features`.

On failing_ref, `rb_autoload_load` does not `rb_const_remove` when the helper does not define the constant. Leftover `Qundef` const_entry. `$LOADED_FEATURES` delete retried leftover autoload. `Module#constants` still had the leftover undefined name (Ruby < 3.1).

Not this packet: specimen-054 cpython generated-code drift. specimen-110 composer leftover abandoned. specimen-157 jest haste leftover mock name. specimen-159 gleam leftover compile cache after move. zeitwerk leftover gem inception (this tick's other packet).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
