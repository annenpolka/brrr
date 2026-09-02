# OBSERVED

Public prisma/prisma#27128 (closed 2025-05-28). PR prisma/orm#27279 squash `8d06a847ea4e84c70c84469b2a845e568f454e14` (parent `23e865c5601534f14cfe5fbc097c2eb1cf4f342e`). Local prisma generate was not performed on this lab host.

Issue body: `prisma generate --watch` runs once correctly, then produces the same generated client regardless of schema.prisma changes. A second terminal `prisma generate` (no watch) writes the current client; the watch process then reverts it to the leftover first-load client.

On failing_ref, `schemaContext` is built once before the watcher. The watch loop does **not** call `getSchemaForGenerate`. That reload is added by PR 27279.

Not this packet: specimen-041 protobuf JSON unknown-fields. specimen-043 protobuf CI generated-code-drift. specimen-136 pants leftover vcs_version process cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
