// Reduced excerpt of LockfileBase on failing_ref
// lockfile/types/src/index.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// PatchFile export removed. Field is hash-only.

export interface LockfileBase {
  lockfileVersion: string
  overrides?: Record<string, string>
  packageExtensionsChecksum?: string
  patchedDependencies?: Record<string, string>
  pnpmfileChecksum?: string
  settings?: LockfileSettings
  time?: Record<string, string>
}
