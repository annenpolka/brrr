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
