KNOWN FIX (sealed): vitest-dev/vitest PR 9077 squash merge e1b2e086a40ce154ae11714fa71749ec21b1ac23.

PR 9076 moved shouldExternalize into fetchAndProcess (after getCachePath) so a memory-cached module skipped a file read. Ordinary externalize then still minted a leftover cache key from file bytes. Repair: call shouldExternalize in fetch immediately after the options?.cached early return and before getCachePath; if externalize, return {externalize, type:'module'} with no key. Cache version bumped 1.0.0-beta.1 → 1.0.0-beta.2 so leftover on-disk names from beta.1 are not reused.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
