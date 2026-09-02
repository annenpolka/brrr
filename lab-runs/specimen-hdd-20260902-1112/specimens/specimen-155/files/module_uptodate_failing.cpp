// Reduced excerpt of IsModuleFileUpToDate on failing_ref
// clang-tools-extra/clangd/ModulesBuilder.cpp
// dc4df5da886e09d36577b3302952bc91b5e7e154
// HSOpts sets ValidateASTInputFilesContent; ASTReader is constructed without it.

HSOpts.ForceCheckCXX20ModulesInputFiles = true;
HSOpts.ValidateASTInputFilesContent = true;
ASTReader Reader(PP, *ModCache, /*ASTContext=*/nullptr,
                 PCHOperations.getRawReader(), CodeGenOpts, {});
// leftover previous BMI after header rewrite
