repository: JetBrains/kotlin
issue: https://github.com/JetBrains/kotlin/pull/6654
pr: https://github.com/JetBrains/kotlin/pull/6654
failing_ref (parent of squash): a05299825cbf5d5e19df97bd7f8ec00a98716871
fixed_ref (dependenciesFingerprint stored and compared): 0a61a56593a0d6270e6e5f66d0fd31c2209429ed
merged_at: 2026-07-14T17:26:08Z
pr_author: homuroll
merged_by: woainikk
changed_files: kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CacheBuilder.kt, kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CachedLibraries.kt, kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CacheStorage.kt, kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/serialization/CacheSerializationSupport.kt
pr_title: Incremental compilation: fixed stale external caches problem
scout_note: not 104/075/103. leftover Native IC after external dep rollback because dependenciesFingerprint omitted. unique vs 001-159.
