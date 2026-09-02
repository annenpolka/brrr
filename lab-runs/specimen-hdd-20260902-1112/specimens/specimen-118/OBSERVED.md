# OBSERVED

Public hashicorp/terraform PR 37396 (merged 2025-08-05). Squash `28cb1307393a2a6a0d1600955e17cd585e1aa7b8` (single parent `dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3`). Changelog: "Fixes resource identity being dropped from state in certain cases". Local terraform was not performed on this lab host.

PR body: two apply paths incorrectly remove resource identity from state. (1) Destroy errors when the provider returns a new non-null state: identity from the provider response is not included. (2) State values do not change during an update, but marks (sensitive) do: Terraform does not call the provider and identity is missing from the copied object.

On failing_ref, the mark-only update object has CreateBeforeDestroy / Dependencies / Private / Status / Value and no Identity field. The error-and-non-null object has Status / Value / Private / CreateBeforeDestroy and no Identity. The success non-null path already has Identity.

`change.AfterIdentity` / `resp.NewIdentity` assignment on those two paths is **not** on the failing revision.

Not this packet: specimen-081 leftover IdentityJSON vs nil identity schema on Decode (PR 37709). specimen-081 is encode/decode of leftover JSON against a nil schema. This packet is identity omitted from the apply-time state object while value remains.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
