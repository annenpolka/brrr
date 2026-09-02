# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Environment Variable Behavior on Windows

**Operational Context:**  
A Windows development environment is present with standard developer tools (compiler, command prompt). The vcpkg source code at commit `e03454a3cffaafbbe5235078b6f2c5bf13ea32bc` exhibits a reported issue where empty environment variables (`FOO=`) are misidentified as unset. The Windows API `GetEnvironmentVariableW` returns `0` for both unset and empty values, merging their identities. The goal is to verify the observed behavior using available tools.

---

### Step 1: Create Minimal Test Program  
Wrote a C++ program (`env_probe.cpp`) to replicate the logic from `get_environment_variable` at the failing commit. The program:  
1. Takes an environment variable name as input.  
2. Uses `GetEnvironmentVariableW` with a null buffer to probe size.  
3. Returns `nullopt` if `sz == 0` or the value otherwise.  

```cpp
// env_probe.cpp
#include <windows.h>
#include <iostream>
#include <string>
#include <optional>

int wmain(int argc, wchar_t* argv[]) {
    if (argc != 2) {
        std::wcerr << L"Usage: env_probe <VAR_NAME>\n";
        return 1;
    }

    const wchar_t* varname = argv[1];
    DWORD sz = GetEnvironmentVariableW(varname, nullptr, 0);
    if (sz == 0) {
        std::wcout << L"nullopt\n";
        return 0;
    }

    std::wstring buffer(sz, L'\0');
    GetEnvironmentVariableW(varname, buffer.data(), sz);
    buffer.resize(sz - 1); // Remove null terminator
    std::wcout << L"Value: [" << buffer << L"]\n";
    return 0;
}
```

Compiled with:  
```powershell
cl.exe /EHsc /nologo env_probe.cpp /link /out:env_probe.exe
```
**Output:**  
```powershell
env_probe.cpp
Microsoft (R) Incremental Linker Version 14.39.33519.0
Copyright (C) Microsoft Corporation.  All rights reserved.

/out:env_probe.exe
env_probe.obj
```

---

### Step 2: Test Scenarios  
Ran `env_probe.exe` for three cases in a clean command prompt:  

#### **Case A: Unset Variable (`FOO` unset)**  
```powershell
set FOO
env_probe.exe FOO
```
**Output:**  
```powershell
Environment variable FOO not defined
nullopt
```
**Observation:**  
Returns `nullopt` as expected.  

#### **Case B: Empty Variable (`FOO=`)**  
```powershell
set FOO=
env_probe.exe FOO
```
**Output:**  
```powershell
nullopt
```
**Observation:**  
Returns `nullopt` instead of an empty string. This matches the reported issue: empty variables are misidentified as unset.  

#### **Case C: Non-Empty Variable (`FOO=bar`)**  
```powershell
set FOO=bar
env_probe.exe FOO
```
**Output:**  
```powershell
Value: [bar]
```
**Observation:**  
Correctly returns the non-empty value.  

---

### Step 3: Direct API Validation  
Used PowerShell to inspect the Windows API behavior:  
```powershell
$varName = "FOO"
# Case B: Set empty
[Environment]::SetEnvironmentVariable($varName, "", "Process")
$nullBufferSize = [Windows.Kernel32]::GetEnvironmentVariable($varName, $null, 0)
"Size when empty: $nullBufferSize"
```
**Output:**  
```powershell
Size when empty: 0
```
**Observation:**  
`GetEnvironmentVariableW` returns `0` for empty variables, identical to unset. This confirms the API-level JOIN.  

---

### Step 4: Error-Code Inspection  
Modified `env_probe.cpp` to capture error codes:  
```cpp
// ... (previous code)
DWORD sz = GetEnvironmentVariableW(varname, nullptr, 0);
DWORD err = GetLastError();
std::wcout << L"Size: " << sz << L", Error: " << err << L"\n";
// ...
```
Recompiled and retested **Case B**:  
```powershell
set FOO=
env_probe.exe FOO
```
**Output:**  
```powershell
Size: 0, Error: 203
nullopt
```
**Observation:**  
Error `203` (`ERROR_ENVVAR_NOT_FOUND`) confirms the API treats empty variables as "not found," merging their identity with unset.  

---

### Conclusions  
1. **Behavior Confirmed:**  
   - At commit `e03454a3cffaafbbe5235078b6f2c5bf13ea32bc`, `get_environment_variable` incorrectly returns `nullopt` for empty environment variables on Windows.  
   - Root cause: `GetEnvironmentVariableW` returns `0` for both unset and empty values, with `ERROR_ENVVAR_NOT_FOUND` in both cases.  

2. **Identity of Case B:**  
   Empty variables (`FOO=`) are treated as **leftover unset** (`nullopt`) due to the API's JOIN.  

3. **Repair Validation:**  
   The fix (post-commit) uses `SetLastError(ERROR_SUCCESS)` and direct buffer probing to distinguish:  
   - `sz == 0` + `ERROR_ENVVAR_NOT_FOUND` → Unset.  
   - `sz == 0` + `ERROR_SUCCESS` → Empty.  

**Recommendation:**  
Audit all callers of `get_environment_variable` to handle empty strings explicitly where needed (e.g., proxy configuration).  

**Next Steps:**  
If further validation is required, reproduce the test in a sandboxed environment with the actual vcpkg-tool binary (avoiding untrusted checkout execution).  

**Final Note:**  
The Windows environment variable API behavior is the underlying constraint. No speculative fixes or novel abstractions were invoked.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
