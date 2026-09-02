repository: llvm/llvm-project
issue: https://github.com/llvm/llvm-project/pull/187653
pr: https://github.com/llvm/llvm-project/pull/187653
failing_ref (parent of squash): dc4df5da886e09d36577b3302952bc91b5e7e154
fixed_ref (ASTReader ValidateASTInputFilesContent): 5ef593b75010301528f665ddbe7d2999165b9238
merged_at: 2026-03-23T03:43:57Z
pr_title: "[clangd] [C++ Modules] Enable content validation for module input files"
scout_note: not bindname / not 075 / not 147. leftover clangd module BMI after header rewrite because ASTReader omitted content validation. unique vs 001-152.
