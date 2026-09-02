KNOWN FIX (sealed): microsoft/vcpkg-tool PR 1997 squash 643c71f3626a7820e48c51d11545711a594dad02.

failing_ref is parent e03454a3cffaafbbe5235078b6f2c5bf13ea32bc.

Windows get_environment_variable treated GetEnvironmentVariableW size 0 as unset. Empty FOO= and unset FOO JOIN to leftover nullopt.

PR repair: distinguish ERROR_ENVVAR_NOT_FOUND from ERROR_SUCCESS empty; callers that want empty-as-absent use get_environment_variable_nonempty.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
