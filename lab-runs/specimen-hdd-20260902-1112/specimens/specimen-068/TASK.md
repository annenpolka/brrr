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
