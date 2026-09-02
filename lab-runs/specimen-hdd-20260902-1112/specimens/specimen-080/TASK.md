# TASK

A package extra `bar` is gated by an environment marker that is false on this interpreter (`python_version < "3"` on 3.14). Install still materializes the extra.

The developer wants to know whether the extra was installed even though its marker failed, and which extra should have been skipped.
