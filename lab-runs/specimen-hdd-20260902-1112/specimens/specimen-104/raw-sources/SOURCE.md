repository: gradle/gradle
issue: https://github.com/gradle/gradle/issues/30052
pr: https://github.com/gradle/gradle/pull/32359
failing_ref (merge first parent): 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
fixed_ref (merge commit): 2f46ab737e15c67d3904602fa66c658258c32b66
second_parent: fa0e3417532e782cc892fcc6cbbf180fb5780038
merged_at: 2025-03-03T15:44:13Z
merged_by: alllex
pr_author: alllex
changed_files: ConfigurableFileCollectionCodec.kt, ConfigurableFileTreeCodec.kt, FileCollectionCodec.kt, PathToFileResolverCodec.kt, RelativePathFilesIntegrationTest.groovy
pr_title: Fix file collections and file trees with relative files under CC
scout_note: not specimen-088 fileTree query observation. Distinct leftover: named FileCollection / provider relative path omits PathToFileResolver so CC load uses leftover root base dir.
