# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

clangd `IsModuleFileUpToDate` can keep the identity of a **previous C++20 module BMI** after a header included by the module unit was rewritten and the BMI should have been different. `HeaderSearchOptions.ValidateASTInputFilesContent` is set true, but `ASTReader` is constructed without `ValidateASTInputFilesContent=true`. StandardCXXModule input files skip content validation. `canReuse` stays true; leftover previous `getValue()` / header bytes stay current.

On failing_ref `dc4df5da886e09d36577b3302952bc91b5e7e154`:

```
HSOpts.ForceCheckCXX20ModulesInputFiles = true;
HSOpts.ValidateASTInputFilesContent = true;
...
ASTReader Reader(PP, *ModCache, /*ASTContext=*/nullptr,
                 PCHOperations.getRawReader(), CodeGenOpts, {});
if (Reader.ReadAST(...) != ASTReader::Success)
  return false;
bool UpToDate = true;
Reader.getModuleManager().visit([&](serialization::ModuleFile &MF) -> bool {
  Reader.visitInputFiles(MF, /*IncludeSystem=*/false, /*Complain=*/false,
      [&](const serialization::InputFile &IF, bool isSystem) {
        if (!IF.getFile() || IF.isOutOfDate())
          UpToDate = false;
      });
  return !UpToDate;
});
return UpToDate;
```

`ASTReader` default skips content validation for StandardCXXModule files unless its own `ValidateASTInputFilesContent` argument is true. HSOpts is not that argument.

Public report (llvm/llvm-project#187653). Module includes `header1.h` (`return 42`); `canReuse` true; rewrite header; leftover previous BMI still reused. In-tree after the repair: ASTReader gets `ValidateASTInputFilesContent=true`; header rewrite is OutOfDate.

Case A — second parse, same header bytes:
  cache identity is current
  not leftover-after-rewrite

Case B — header rewritten, leftover BMI:
  leftover: previous module / previous header bytes
  ASTReader content validation omitted
  canReuse true

Case C — rebuild modules / no prior BMI:
  fresh module identity
  not leftover previous BMI

Case D — ValidateASTInputFilesContent on ASTReader (post-repair shape, not on failing_ref):
  new BMI after header rewrite
  not leftover previous module

The developer wants to know which identity case B actually used for the module after the header rewrite: leftover previous-BMI (content validation omitted), current header bytes, or omitted (no module cache).

# OBSERVED

Public llvm/llvm-project#187653 (merged 2026-03-23). Squash `5ef593b75010301528f665ddbe7d2999165b9238` (parent `dc4df5da886e09d36577b3302952bc91b5e7e154`). Local clangd was not performed on this lab host.

PR body: IsModuleFileUpToDate did not properly validate input files for C++20 modules. ASTReader skips StandardCXXModule input validation unless ForceCheckCXX20ModulesInputFiles and ValidateASTInputFilesContent are both set on the reader. Test: header change in a module unit must be detected.

On failing_ref, HSOpts sets the flags but ASTReader is constructed with defaults `{}`. visitInputFiles mtime/out-of-date does not content-hash the header.

Not this packet: specimen-013 bindname last-wins. specimen-075 rustc incremental. specimen-147 CDK truncated mtime.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref dc4df5da886e09d36577b3302952bc91b5e7e154
# clang-tools-extra/clangd/ModulesBuilder.cpp IsModuleFileUpToDate

# public shape:
# leftover C++20 module BMI after header rewrite
# ASTReader constructed without ValidateASTInputFilesContent
# rebuild / reader flag yields a new BMI
```

Source-backed only. Do not execute untrusted checkouts on the host.

llvm/llvm-project
  clang-tools-extra/clangd/ModulesBuilder.cpp

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  clangd C++20 prerequisite module BMI
  leftover BMI after header rewrite

Case A (second parse, same header bytes):
  current cache identity
  not leftover-after-rewrite

Case B (header rewritten, leftover BMI):
  leftover: previous module / previous header bytes
  ASTReader content validation omitted
  canReuse true

Case C (rebuild modules / no prior BMI):
  fresh module identity
  not leftover previous BMI

Case D (ValidateASTInputFilesContent on ASTReader):
  new BMI after header rewrite
  not leftover previous module

Not this packet:
  bindname last-wins (specimen-013)
  rustc incremental fingerprint (specimen-075)

### module_uptodate_failing.cpp

// Reduced excerpt of IsModuleFileUpToDate on failing_ref
// clang-tools-extra/clangd/ModulesBuilder.cpp
// dc4df5da886e09d36577b3302952bc91b5e7e154
// HSOpts sets ValidateASTInputFilesContent; ASTReader is constructed without it.

HSOpts.ForceCheckCXX20ModulesInputFiles = true;
HSOpts.ValidateASTInputFilesContent = true;
ASTReader Reader(PP, *ModCache, /*ASTContext=*/nullptr,
                 PCHOperations.getRawReader(), CodeGenOpts, {});
// leftover previous BMI after header rewrite

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
