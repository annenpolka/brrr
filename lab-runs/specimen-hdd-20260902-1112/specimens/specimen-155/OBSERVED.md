# OBSERVED

Public llvm/llvm-project#187653 (merged 2026-03-23). Squash `5ef593b75010301528f665ddbe7d2999165b9238` (parent `dc4df5da886e09d36577b3302952bc91b5e7e154`). Local clangd was not performed on this lab host.

PR body: IsModuleFileUpToDate did not properly validate input files for C++20 modules. ASTReader skips StandardCXXModule input validation unless ForceCheckCXX20ModulesInputFiles and ValidateASTInputFilesContent are both set on the reader. Test: header change in a module unit must be detected.

On failing_ref, HSOpts sets the flags but ASTReader is constructed with defaults `{}`. visitInputFiles mtime/out-of-date does not content-hash the header.

Not this packet: specimen-013 bindname last-wins. specimen-075 rustc incremental. specimen-147 CDK truncated mtime.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
