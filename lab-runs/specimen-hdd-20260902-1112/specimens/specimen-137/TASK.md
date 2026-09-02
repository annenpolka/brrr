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
