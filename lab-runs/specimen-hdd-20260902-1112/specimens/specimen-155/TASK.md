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
