CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public microsoft/vcpkg-tool#1997 (merged 2026-05-12). Squash `643c71f3626a7820e48c51d11545711a594dad02` (parent `e03454a3cffaafbbe5235078b6f2c5bf13ea32bc`). Follow-up of #1988 (empty HTTPS_PROXY / NO_PROXY treated as unset). Local vcpkg-tool was not performed on this lab host.

PR title: Fix empty vs. unset environment variables on Windows. Same defect as #1988 on the normal getenv path. Audit callers.

On failing_ref, Windows `GetEnvironmentVariableW(..., nullptr, 0)` returning 0 is treated as unset. Empty `FOO=` and unset FOO JOIN. POSIX getenv already distinguishes NULL vs empty.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty user `proxy =` vs global. specimen-149 compose listed-without-equals vs image ENV. specimen-150 systemd `::` cwd search path.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
# src/vcpkg/base/system.cpp get_environment_variable

# public shape:
# leftover unset after FOO= empty on Windows
# GetEnvironmentVariableW sz==0 JOINs empty and unset
# FOO=bar is a present string; POSIX getenv already splits
```

Source-backed only. Do not execute untrusted checkouts on the host.

microsoft/vcpkg-tool
  src/vcpkg/base/system.cpp
  src/vcpkg-test/system.cpp
  include/vcpkg/base/system.h

RELEVANT MATERIAL

### getenv_failing.cpp

// Reduced excerpt of get_environment_variable on failing_ref
// src/vcpkg/base/system.cpp
// e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
// Windows size-zero probe JOINs empty FOO= and unset FOO into leftover nullopt.

Optional<std::string> get_environment_variable(ZStringView varname)
{
#if defined(_WIN32)
    const auto w_varname = Strings::to_utf16(varname);
    const auto sz = GetEnvironmentVariableW(w_varname.c_str(), nullptr, 0);
    if (sz == 0) return nullopt;
    std::wstring ret(sz, L'\0');
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

### leftover_identity_split.txt

Registry / fixture:
  vcpkg get_environment_variable Windows
  leftover unset after empty FOO= JOIN

Case A (FOO unset):
  unset identity
  not leftover-empty-as-unset

Case B (FOO= empty string, leftover JOIN):
  leftover: unset / nullopt
  GetEnvironmentVariableW sz==0

Case C (FOO=bar present):
  current string identity
  not leftover unset

Case D (empty present kept):
  has_value empty string
  not leftover unset

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  pip empty user proxy vs global (specimen-031)
  compose listed-without-equals vs image ENV (specimen-149)
  systemd empty :: cwd search path (specimen-150)

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
