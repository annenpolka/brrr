# COMMANDS

```
# in-tree on failing_ref e345cc58ecad0e1e18eefc00638d7fa32966c2b7
# (not executed on this lab host)

# case A — never nested-overridden
# package.json dependencies: json-server ^0.17.0; no overrides
npm install
# lockfile identity of package-json is json-server's original range
# npm audit reports that original identity's vulnerabilities
# no overridden annotation for package-json

# case B — first install, empty stores, nested override present
# package.json overrides.json-server.package-json = 7.0.0
rm -rf node_modules package-lock.json
npm install
# npm audit: 0 vulnerabilities
# lockfile identity of package-json is 7.0.0

# case C — leftover original identity; nested override still in package.json
npm install
# npm audit: 5 vulnerabilities
# lockfile identity of package-json matches case A, not 7.0.0

# public #5850 variants
# npm update                          → 0 vulnerabilities
# rm -rf node_modules && npm install  → 5 vulnerabilities
# rm package-lock.json && npm install → 5 vulnerabilities

# case D — in-tree: detach the override-carrying incoming edge
# baz.overrides still the leftover set
# baz.edgesOut.get('buzz').overrides still names that set
# Edge.detach only ran edgesIn.delete

# unit tests live in workspaces/arborist/test/node.js
# production paths: workspaces/arborist/lib/node.js (addEdgeIn)
#                   workspaces/arborist/lib/edge.js (reload, detach)
```

Not executed on this lab host.
