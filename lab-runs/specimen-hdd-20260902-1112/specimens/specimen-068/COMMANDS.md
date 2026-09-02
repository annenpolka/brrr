# COMMANDS

```
pnpm runtime set node 24 -g
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
file "$(command -v node)"
head "$(command -v node)"
```

Not executed on this lab host.
