repository: gradle/gradle
issue: https://github.com/gradle/gradle/issues/36392
pr: https://github.com/gradle/gradle/pull/38432
failing_ref (parent of relocate-check commit on master): e0ca283b48bc739f14140b8a61565d689758c032
fixed_ref (Don't use CC if it's relocated): 24311263532f820ba81399b662ae3d53eebe28b9
merged_at: 2026-07-13T14:26:08Z
pr_author: ov7a
merged_by: ov7a
changed_files: DefaultConfigurationCache.kt, ConfigurationCacheDirIntegrationTest.groovy
pr_title: Don't use CC if it's relocated
scout_note: not specimen-104 ccnamed leftover root base dir (resolver omitted). not specimen-088 fileTree query. Distinct leftover: CC identity omits build location so leftover named-file absolute paths from the previous directory are reused after copy/move. job-0531 was coord-skipped as already 104; this axis is leftover named-file abs paths after relocate, not leftover resolver for relative named files.
