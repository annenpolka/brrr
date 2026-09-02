// Reduced excerpt of getHmrRefreshHash on failing_ref
// packages/next/src/server/app-render/work-unit-async-storage.external.ts
// 70f8b678877ba69f266e1522fcfacb95cfd3c76e
// request path reads the HMR cookie; server hash omitted.

export function getHmrRefreshHash(
  workUnitStore: WorkUnitStore
): string | undefined {
  if (process.env.__NEXT_DEV_SERVER) {
    switch (workUnitStore.type) {
      case 'cache':
      case 'private-cache':
      case 'prerender':
      case 'prerender-runtime':
        return workUnitStore.hmrRefreshHash
      case 'request':
        return workUnitStore.cookies.get(NEXT_HMR_REFRESH_HASH_COOKIE)?.value
    }
  }
  return undefined
}
