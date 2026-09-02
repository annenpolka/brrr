# Reduced excerpt of multidispatch cache lookup on failing_ref
# src/compiler/crystal/interpreter/multidispatch.cr
# leftover HIT when a later site shares obj_type+signature.

cache_key = Context::MultidispatchKey.new(obj_type, signature)
cached_def = context.multidispatchs[cache_key]?
return cached_def if cached_def
