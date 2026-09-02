KNOWN FIX (sealed): moonrepo/moon PR 482 squash 2959d6f0bcc9dbe12fb3f35e54186d245b44586a.

failing_ref is parent 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199.

expand_env loaded dotenv into env vars but omitted the env file from inputs; get_file_hashes skipped gitignored paths, so leftover cache after a .env change kept previous-env task output.

PR repair: push env_file onto inputs; hash task inputs with allow_ignored=true.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
