KNOWN FIX (sealed): prisma/orm PR 27279 squash 8d06a847ea4e84c70c84469b2a845e568f454e14.

failing_ref is parent 23e865c5601534f14cfe5fbc097c2eb1cf4f342e.

prisma generate --watch reused leftover schemaContext from the first load, so leftover generated client after a schema.prisma change kept previous models.

PR repair: re-run getSchemaForGenerate + processSchemaResult + inferDirectoryConfig inside the watch loop.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
