# OBSERVED

Public pnpm/pnpm#10911 (merged): lockfile `patchedDependencies` simplified from `Record<string, { path: string, hash: string }>` to `Record<string, string>` (selector → hash). Patch file paths come from user config (`opts.patchedDependencies`), not from the lockfile.

Downstream (0x80/isolate-package#201 / #202): `@pnpm/lockfile-file` passes the field through unchanged, so a pnpm 11 lockfile yields bare hash strings instead of `{ path, hash }` objects. `copyPatches` only read `originalPatchFile?.hash`, which is undefined for a string entry, so the isolated lockfile wrote an **empty** hash. pnpm then rejected frozen install: `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH`.

This packet is an owned two-shape fixture of those identities. It does not include a local pnpm checkout. Do not execute untrusted checkouts on the host. Not specimen-068 (Unix node env-hop).
