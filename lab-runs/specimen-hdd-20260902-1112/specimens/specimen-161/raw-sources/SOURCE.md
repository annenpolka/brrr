repository: vercel/next.js
issue: https://github.com/vercel/next.js/pull/96022
pr: https://github.com/vercel/next.js/pull/96022
failing_ref (parent of squash on canary): 70f8b678877ba69f266e1522fcfacb95cfd3c76e
fixed_ref (server-authored HMR hash, cookie removed): 286862e35bbc4fa7c023077cf794d5852063463a
merged_at: 2026-07-22T13:50:26Z
pr_author: unstubbable
merged_by: unstubbable
changed_files: packages/next/src/server/app-render/work-unit-async-storage.external.ts, packages/next/src/server/use-cache/use-cache-wrapper.ts, packages/next/src/client/dev/hot-reloader/app/hot-reloader-app.tsx, packages/next/src/server/base-server.ts, packages/next/src/server/request-meta.ts, test/e2e/app-dir/use-cache-dev/use-cache-dev.test.ts
pr_title: Fix stale dev `'use cache'` for cookieless requests and route handlers
scout_note: not 090/156/157. leftover 'use cache' after edit because request path omitted server HMR hash. unique vs 001-159.
