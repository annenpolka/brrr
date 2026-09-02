// Reduced excerpt of patching/types on failing parent
// patching/types/src/index.ts
// 60d3a328bc047c211f75936d54003323ee7ee245

export interface PatchFile {
  path: string
  hash: string
}

export interface PatchInfo {
  file: PatchFile
}
