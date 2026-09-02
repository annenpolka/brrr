repository: crystal-lang/crystal
issue: https://github.com/crystal-lang/crystal/issues/16810
pr: https://github.com/crystal-lang/crystal/pull/16958
failing_ref (parent of squash on master): c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
fixed_ref (target_def_ids added to MultidispatchKey): ac82b6ba7dcdc83f72199e8827f68417d61b88c4
merged_at: 2026-05-20T15:48:57Z
pr_author: stakach
merged_by: straight-shoota
changed_files: spec/compiler/interpreter/multidispatch_spec.cr, src/compiler/crystal/interpreter/context.cr, src/compiler/crystal/interpreter/multidispatch.cr
pr_title: Fix interpreter multidispatch cache collision
scout_note: not 054/154/159. leftover multidispatch chain after new type because target_def ids omitted. unique vs 001-159.
