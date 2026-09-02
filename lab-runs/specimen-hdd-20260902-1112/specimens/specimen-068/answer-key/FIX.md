KNOWN FIX (sealed): pnpm/pnpm PR 14420 squash 22d0067d3786ed9892432d962428269fa91c7495.

Pacquet's Unix global node was a POSIX shell shim; Dash dropped env names that are not shell identifiers before exec. Repair: use the native dispatcher already used on Windows (argv0-detected, fallback path in .pnpm-shim-v1-node-target) on Unix as well, so Node inherits TEST-VAR and Actions kebab-case inputs.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
