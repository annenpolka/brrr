repository: dart-lang/pub
issue: https://github.com/dart-lang/sdk/issues/61950
pr: https://github.com/dart-lang/pub/pull/4863
failing_ref (parent of squash on master): 425174668513d0696a637e62c683ec5885999914
fixed_ref (Use workspace root when constructing Entrypoint): 0382a52acba89ff0080d559bb22f4017962bbd1d
merged_at: 2026-09-01T13:49:04Z
pr_author: sigurdm
merged_by: sigurdm
changed_files: lib/src/entrypoint.dart, lib/src/executable.dart, test/embedding/get_executable_for_command.dart
pr_title: Use workspace root when constructing Entrypoint in getExecutableForCommand and ensureUpToDate
scout_note: not specimen-103 go-work leftover replace. not 121 swift registry TTL. Distinct leftover: package_config identity omits missing workspace members so leftover mapping without pkg_b is treated as current. job-0538 unique vs 001-127 (no dart-lang/pub).
