KNOWN FIX (sealed): stylelint/stylelint PR 6356 squash 5be33b779b93761d86cb871dfd70f34686b5f6c5.

failing_ref is parent 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66.

standalone hashed JSON.stringify(config || {}) before cosmiconfig resolution, so leftover cache after a config-file change kept previous-config lint results.

PR repair: calcHashOfConfig on the resolved config inside lintSource after getConfigForFile.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
