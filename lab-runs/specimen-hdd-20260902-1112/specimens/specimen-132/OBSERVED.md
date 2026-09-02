# OBSERVED

Public eslint/eslint#16284 (closed 2023-03-23). PR 16992 squash `1665c029acb92bf8812267f1647ad1a7054cbcb4` (parent `b3634f695ddab6a82c0a9b1d8695e62b60d23366`). Local ESLint was not performed on this lab host.

Issue body: leftover cache after eslint-plugin-react upgrade hid new-rule offenses. Related eslintrc#88 is not this packet (legacy eslintrc cache).

On failing_ref, `toJSON` serializes plugins as `Object.keys(plugins)` only. `getObjectId` for plugins is **not** on the failing revision. It is added by PR 16992.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-128 dart leftover package_config missing workspace member.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
