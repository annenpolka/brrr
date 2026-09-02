KNOWN FIX (sealed): llvm/llvm-project PR 187653 squash 5ef593b75010301528f665ddbe7d2999165b9238.

failing_ref is parent dc4df5da886e09d36577b3302952bc91b5e7e154.

IsModuleFileUpToDate set ValidateASTInputFilesContent on HeaderSearchOptions but constructed ASTReader with defaults, so StandardCXXModule input files skipped content validation. Leftover previous BMI after header rewrite.

PR repair: pass ValidateASTInputFilesContent=true into ASTReader; ReadAST ARR_OutOfDate.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
