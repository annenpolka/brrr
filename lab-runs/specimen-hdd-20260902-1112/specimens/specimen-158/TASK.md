# TASK

vcpkg `get_environment_variable` on Windows can keep the identity of **unset** after the process listed `FOO=` (equals, empty string) and that listing should have meant present-and-empty. `GetEnvironmentVariableW` returns size `0` for both ERROR_ENVVAR_NOT_FOUND and a present empty value. The JOIN of empty and unset is one leftover identity.

On failing_ref `e03454a3cffaafbbe5235078b6f2c5bf13ea32bc`:

```
Optional<std::string> get_environment_variable(ZStringView varname)
{
#if defined(_WIN32)
    const auto w_varname = Strings::to_utf16(varname);
    const auto sz = GetEnvironmentVariableW(w_varname.c_str(), nullptr, 0);
    if (sz == 0) return nullopt;

    std::wstring ret(sz, L'\0');
    Checks::check_exit(VCPKG_LINE_INFO, MAXDWORD >= ret.size());
    const auto sz2 = GetEnvironmentVariableW(w_varname.c_str(), ret.data(), static_cast<DWORD>(ret.size()));
    Checks::check_exit(VCPKG_LINE_INFO, sz2 + 1 == sz);
    ret.pop_back();
    return Strings::to_utf8(ret.c_str());
#else
    auto v = getenv(varname.c_str());
    if (!v) return nullopt;
    return std::string(v);
#endif
}
```

`sz == 0` is the JOIN. Unset is `nullopt`. Empty `FOO=` is also `nullopt`. A present `FOO=bar` is a string. POSIX `getenv` already splits NULL vs `""`; the Windows size-zero probe does not.

Public report (microsoft/vcpkg-tool#1997), follow-up of #1988 (`HTTPS_PROXY` / `NO_PROXY` empty vs unset). Tests after the repair: unset → no value; `FOO=` → has_value and empty string; `FOO=x` → `x`. Callers that want empty-as-absent use a separate helper after the repair.

In-tree after the repair (not on failing_ref): `SetLastError(ERROR_SUCCESS)` then `GetEnvironmentVariableW` into an SSO buffer; `sz == 0` with `ERROR_ENVVAR_NOT_FOUND` is unset; `sz == 0` with `ERROR_SUCCESS` is empty present.

Case A — `FOO` unset (`ERROR_ENVVAR_NOT_FOUND`):
  unset identity
  not leftover-empty-as-unset

Case B — `FOO=` empty string, leftover JOIN:
  leftover: unset / `nullopt`
  Windows size-zero probe
  same process lookup

Case C — `FOO=bar` present:
  current string identity
  not leftover unset

Case D — empty present kept (post-repair shape, not on failing_ref):
  has_value empty string
  not leftover unset

The developer wants to know which identity case B actually used for `FOO` after listing `FOO=`: leftover unset (`sz==0` JOIN), current empty string, or omitted (no getenv).
