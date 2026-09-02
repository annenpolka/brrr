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
