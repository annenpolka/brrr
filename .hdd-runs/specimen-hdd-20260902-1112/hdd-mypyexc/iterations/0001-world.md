# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

mypy `--incremental` can keep the identity of a **previous cache result** after `--untyped-calls-exclude` should have been a different check. `OPTIONS_AFFECTING_CACHE` listed platform/plugins/strict_bytes/fixed_format_cache. `untyped_calls_exclude` is omitted.

On failing_ref `8f2371a565eb9c29f03922b26da8eab054fbbcf8`:

```
OPTIONS_AFFECTING_CACHE: Final = (
    PER_MODULE_OPTIONS
    | {
        "platform",
        "bazel",
        "old_type_inference",
        "plugins",
        "disable_bytearray_promotion",
        "disable_memoryview_promotion",
        "strict_bytes",
        "fixed_format_cache",
    }
) - {"debug_cache"}
```

`self.untyped_calls_exclude: list[str] = []` exists as an option. It is not in OPTIONS_AFFECTING_CACHE.

Public report (python/mypy#16652). `--disallow-untyped-calls --untyped-calls-exclude=bug.Super` errors; `--untyped-calls-exclude=bug` succeeds; a later `--untyped-calls-exclude=bug.Super` with leftover `.mypy_cache` also succeeds until `rmdir .mypy_cache`.

In-tree after the repair (not on failing_ref): `"untyped_calls_exclude"` is a member of OPTIONS_AFFECTING_CACHE. Test `testUntypedCallsExcludeAffectsCache`.

Case A — second mypy with unchanged --untyped-calls-exclude:
  cache identity is current
  not leftover-after-exclude-change

Case B — exclude string flipped, leftover .mypy_cache:
  leftover: previous success/error identity
  untyped_calls_exclude omitted from OPTIONS_AFFECTING_CACHE
  Super-exclude after bug-exclude stays success

Case C — rmdir .mypy_cache then Super-exclude:
  fresh cache identity
  error on untyped draw

Case D — untyped_calls_exclude in OPTIONS_AFFECTING_CACHE (post-repair shape, not on failing_ref):
  cache miss after exclude change
  not leftover previous success

The developer wants to know which identity case B actually used for the incremental cache after the exclude change: leftover previous-exclude results (flag omitted from OPTIONS_AFFECTING_CACHE), current exclude identity, or omitted (no cache).

# OBSERVED

Public python/mypy#16652 (closed 2025-09-06). PR 19801 merge `309b01e287e3afabeb888572455f9bf55d86acad` (parent `8f2371a565eb9c29f03922b26da8eab054fbbcf8`). Local mypy was not performed on this lab host.

Issue body: same command different results depending on leftover cache; Super-exclude errors on a cold cache; after a successful `bug` exclude run, Super-exclude succeeds until `.mypy_cache` is deleted.

On failing_ref, OPTIONS_AFFECTING_CACHE ends at `fixed_format_cache`. `untyped_calls_exclude` is **not** in that set. It is added by PR 19801.

Not this packet: specimen-067 mypy leftover sentinels (issue 21866 / PR 21888 expandtype). specimen-075 rustc incremental. specimen-136 pants vcs_version process cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 8f2371a565eb9c29f03922b26da8eab054fbbcf8
# mypy/options.py OPTIONS_AFFECTING_CACHE

# public shape:
# leftover .mypy_cache after --untyped-calls-exclude change
# untyped_calls_exclude omitted from OPTIONS_AFFECTING_CACHE
# Super-exclude after bug-exclude stays success until rmdir .mypy_cache
```

Source-backed only. Do not execute untrusted checkouts on the host.

python/mypy
  mypy/options.py
  test-data/unit/check-incremental.test
  .mypy_cache

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  --disallow-untyped-calls --untyped-calls-exclude
  leftover .mypy_cache after exclude string change

Case A (second mypy, same exclude):
  current cache identity
  not leftover-after-exclude-change

Case B (exclude flipped Super -> bug -> Super, leftover cache):
  leftover: previous success identity
  untyped_calls_exclude omitted from OPTIONS_AFFECTING_CACHE
  Super-exclude stays success

Case C (rmdir .mypy_cache):
  fresh cache identity
  Super-exclude errors

Case D (untyped_calls_exclude in OPTIONS_AFFECTING_CACHE):
  cache miss after exclude change
  not leftover previous success

Not this packet:
  mypy leftover sentinels (specimen-067)
  rustc incremental (specimen-075)
  pants vcs_version process cache (specimen-136)

### options_affecting_cache_failing.py

# Reduced excerpt of OPTIONS_AFFECTING_CACHE on failing_ref
# mypy/options.py
# 8f2371a565eb9c29f03922b26da8eab054fbbcf8
# untyped_calls_exclude omitted from the cache-identity set.

OPTIONS_AFFECTING_CACHE: Final = (
    PER_MODULE_OPTIONS
    | {
        "platform",
        "bazel",
        "old_type_inference",
        "plugins",
        "disable_bytearray_promotion",
        "disable_memoryview_promotion",
        "strict_bytes",
        "fixed_format_cache",
        # no "untyped_calls_exclude"
    }
) - {"debug_cache"}

# option exists; not hashed into cache identity
self.untyped_calls_exclude: list[str] = []

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
