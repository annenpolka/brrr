# TASK

An ordered index insert reports success when adding a name that collides with a directory prefix, but only if the insertion position is not zero. Tests that seed a single earlier entry never catch it. The developer wants to know why exit status 0 is lying and which entries still collide.
