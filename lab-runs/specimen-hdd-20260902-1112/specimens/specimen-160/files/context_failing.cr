# Reduced excerpt of Context::MultidispatchKey on failing_ref
# src/compiler/crystal/interpreter/context.cr
# c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
# key is (obj_type, call_signature); target_def ids omitted.

record MultidispatchKey, obj_type : Type, call_signature : CallSignature
