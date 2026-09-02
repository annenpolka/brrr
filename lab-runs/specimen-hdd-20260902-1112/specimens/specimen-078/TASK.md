# TASK

A test cache keys freshness by the test file list only. First run builds with binary buildid `buildid-aaa`. The binary is rewritten with `buildid-bbb`. Second run reports FRESH because the cache key ignored buildid.

The developer wants to know whether the cache key included the binary buildid, and whether FRESH reused a stale binary.
