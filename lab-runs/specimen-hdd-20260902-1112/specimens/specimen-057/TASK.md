# TASK

Outer parser ignore_unknown=true. Nested Any-like payload is parsed by an inner instance whose options default ignore_unknown=false. Unknown field errors on the inner instance.

The developer wants to know which instance ran and whether the outer flag applied.
