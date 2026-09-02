# TASK

Home Assistant pytest collection: a parent directory appears more than once in the argument list. Fixtures registered from conftest are “not found” for tests collected after unrelated paths. Order of CLI path arguments changes whether fixtures resolve.

The developer wants to know whether the same directory is still the same collection object, and which fixture definitions are bound to which object identities.
