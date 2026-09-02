repository: sbt/sbt
issue: https://github.com/sbt/sbt/issues/9195
pr: https://github.com/sbt/sbt/pull/9207
failing_ref (merge first parent): c491f035f832a62843d69364b55237dc29c99e7d
fixed_ref (merge commit): 49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef
second_parent: e69e23aae14240d2c6b63e2c5ff356ccc154e784
merged_at: 2026-05-11T14:20:27Z
pr_author: eed3si9n
merged_by: eed3si9n
changed_files: main/src/main/scala/sbt/Defaults.scala, main/src/main/scala/sbt/internal/BuildDef.scala, project/Dependencies.scala, scripted tests
pr_title: [2.x] fix: Fixes cache restoration of incremental compilation state (Analysis)
scout_note: not specimen-088/104 gradle CC leftover. not 075 rustc incremental. Distinct leftover: extra last-write zinc Analysis identity vs current analysis-file identity (size+mtime) after gz switch. job-0469 unique vs 001-111 (no sbt).
