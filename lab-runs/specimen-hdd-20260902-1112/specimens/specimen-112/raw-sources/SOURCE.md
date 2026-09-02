repository: composer/composer
issue: https://github.com/composer/composer/issues/12417
pr: https://github.com/composer/composer/pull/12423
failing_ref (squash parent / PR base): aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
fixed_ref (squash merge): 1a22bb197a6e62ca431928627ef232bd4d335097
merged_at: 2025-09-18T09:46:16Z
pr_author: Seldaek
merged_by: Seldaek
changed_files: src/Composer/DependencyResolver/Transaction.php, tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test, tests/Composer/Test/Fixtures/installer/update-syncs-outdated.test
pr_title: Ensure packages where the abandoned state changes get reinstalled to sync up the state in installed.json
scout_note: not specimen-074/021/086. Distinct leftover: installed.json omitted abandoned while lock has abandoned. job-0458.
