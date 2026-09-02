repository: prisma/orm
issue: https://github.com/prisma/prisma/issues/27128
pr: https://github.com/prisma/orm/pull/27279
failing_ref (parent of squash on main): 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
fixed_ref (reload schema in watch generate): 8d06a847ea4e84c70c84469b2a845e568f454e14
merged_at: 2025-05-28T17:14:02Z
pr_author: aqrln
merged_by: aqrln
changed_files: packages/cli/src/Generate.ts, packages/client/tests/e2e/27128-generate-watch/*
pr_title: fix(cli): reload the schema when generating the client in watch mode
scout_note: not 041/043 protobuf generated-drift. Distinct leftover: watch loop keeps first-load schemaContext so leftover generated client after schema.prisma change is treated as current. job-0588 was SKIP prisma/prisma unsearchable; pair is prisma/orm#27279.
