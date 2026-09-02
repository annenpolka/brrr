repository: npm/cli
issue: https://github.com/npm/cli/issues/5850
pr: https://github.com/npm/cli/pull/8089
related_pr: https://github.com/npm/cli/pull/7025
failing_ref (squash merge parent): e345cc58ecad0e1e18eefc00638d7fa32966c2b7
fixed_ref (squash merge commit): b9225e524074239bd8db9a27f3e9ab72f2b5c09e
head_sha: 9feb44c99f06bb4ca83abbefa3174e5e1654227f
merged_at: 2025-02-26T17:12:42Z
merged_by: wraithgar
changed_files: workspaces/arborist/lib/dep-valid.js, workspaces/arborist/lib/edge.js, workspaces/arborist/lib/node.js, workspaces/arborist/lib/override-set.js, workspaces/arborist/tap-snapshots/test/edge.js.test.cjs, workspaces/arborist/test/edge.js, workspaces/arborist/test/node.js, workspaces/arborist/test/override-set.js
pr_title: fix: resolve override conflicts and apply correct versions
scout_note: not specimen-004/033 optional-peer packument fetch (npm/cli#9876). not specimen-082/Honor-KILL peerleft (bun.lock leftover packages vs optionalPeers mention after bun remove). not #8986 leftover overridden lockfile identity after deleting the overrides field (open, no fixed_ref). not #9359 leftover generic OverrideSet forwarded through a Link with no matching rule. Distinct leftover: nested override json-server.package-json=7.0.0 honored only on empty-store first install / npm update; subsequent npm install returns original package-json identity. In-tree: addEdgeIn overwrites this.overrides; detach/reload delete the incoming edge without recomputing the target OverrideSet, so out-edges keep the leftover rule.
