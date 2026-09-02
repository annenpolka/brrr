repository: biomejs/biome
issue: https://github.com/biomejs/biome/pull/11409
pr: https://github.com/biomejs/biome/pull/11409
failing_ref (parent of squash): 7dbf9d84125b51c4177a899f8638d54b01cd065c
fixed_ref (db_remove_file on close; files map on WorkspaceDbData): 405dedb0ff65dd29927faf587f6542e3c29db248
merged_at: 2026-08-19T18:25:28Z
pr_author: ematipico
merged_by: ematipico
changed_files: crates/biome_service/src/db/mod.rs, crates/biome_service/src/db/state.rs, crates/biome_service/src/workspace/server.rs, crates/biome_service/src/workspace/server.tests.rs, .changeset/fix-workspace-db-file-cache-eviction.md
pr_title: fix(core): files eviction and project
scout_note: not 157/159. leftover parsed source after close because files map omitted from eviction. unique vs 001-163.
