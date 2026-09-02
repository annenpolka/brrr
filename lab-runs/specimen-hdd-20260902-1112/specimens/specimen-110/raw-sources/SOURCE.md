repository: composer/composer
issue: https://github.com/composer/composer/issues/12417
pr: https://github.com/composer/composer/pull/12423
failing_ref (squash parent): 8fc94c5e9972d2ebb87e57711a8477392b30f299
fixed_ref (squash merge): 1a22bb197a6e62ca431928627ef232bd4d335097
merged_at: 2025-09-18T09:46:16Z
pr_author: Seldaek
merged_by: Seldaek
changed_files: src/Composer/DependencyResolver/Transaction.php, tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test, tests/Composer/Test/Fixtures/installer/update-syncs-outdated.test
pr_title: Ensure packages where the abandoned state changes get reinstalled to sync up the state in installed.json
scout_note: not specimen-021/074. Distinct leftover: installed.json abandoned-state identity omitted after lock already recorded abandoned for the same version. job-0458.
