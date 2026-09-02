CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

`pnpm runtime set node --global` on Unix puts a `node` on PATH. Launching it drops environment entries whose names are not valid shell identifiers.

```
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# outputs MISSING
```

The real Node binary at the managed store path, invoked the same way, prints `123`.

GitHub/Gitea/Forgejo Actions pass parameters as kebab-case env names (`INPUT-FOO`). Self-hosted runners using this `node` see those inputs as missing.

The TypeScript CLI's global Node link on Unix already preserves those names. The pacquet (Rust) Unix entry does not.

The developer wants to know which process actually exec'd Node, and which environment names survived that hop.

# OBSERVED

Public pnpm/pnpm#14417 / PR 14420. Failing world: pacquet Unix global `node` is a POSIX shell shim (`# pnpm-shim-style=context-aware`, contains `--shim 'node'`). Windows already used a native dispatcher plus sibling target file `.pnpm-shim-v1-node-target`.

POSIX (Dash) initializes shell variables from the environment only when the name is a valid identifier. Names with `-` are unspecified for inheritance into the child. The shim's `exec` therefore launches Node without `TEST-VAR`.

Direct execution of the managed binary (same inode as the store copy) inherits the full environment, including `TEST-VAR=123`.

Reporter container:

```
docker run -it --rm ghcr.io/pnpm/pnpm
pnpm runtime set node 24 -g
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# MISSING
env 'TEST-VAR=123' ${REAL_NODE} -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# 123
```

In-tree failing assertion shape (Unix): the global `node` file is readable as text and contains `--shim 'node'` / `# pnpm-shim-style=context-aware`.

This packet does not include a local clone; treat the snippets as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
pnpm runtime set node 24 -g
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
file "$(command -v node)"
head "$(command -v node)"
```

Not executed on this lab host.

pnpm/pnpm
  pnpm/crates/cli/src/shim_dispatch.rs
  pnpm/crates/cmd-shim/src/link_bins.rs
  pnpm/crates/cli/tests/suite/global.rs

RELEVANT MATERIAL

### repro_env.txt

env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# via PATH node (shell shim): MISSING
# via REAL_NODE (managed binary): 123

### unix_node_shim.excerpt.sh

#!/bin/sh
# pnpm-shim-style=context-aware
# Reduced shape of the Unix global `node` entry on the failing revision.
# A POSIX shell only copies env names that are valid identifiers into
# its own variable table before exec.
exec /pnpm/global/v11/.../node_modules/node/bin/node --shim 'node' "$@"

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
