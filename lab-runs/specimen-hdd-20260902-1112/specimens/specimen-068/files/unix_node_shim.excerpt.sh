#!/bin/sh
# pnpm-shim-style=context-aware
# Reduced shape of the Unix global `node` entry on the failing revision.
# A POSIX shell only copies env names that are valid identifiers into
# its own variable table before exec.
exec /pnpm/global/v11/.../node_modules/node/bin/node --shim 'node' "$@"
