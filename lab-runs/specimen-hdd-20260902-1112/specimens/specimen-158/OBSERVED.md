# OBSERVED

Public microsoft/vcpkg-tool#1997 (merged 2026-05-12). Squash `643c71f3626a7820e48c51d11545711a594dad02` (parent `e03454a3cffaafbbe5235078b6f2c5bf13ea32bc`). Follow-up of #1988 (empty HTTPS_PROXY / NO_PROXY treated as unset). Local vcpkg-tool was not performed on this lab host.

PR title: Fix empty vs. unset environment variables on Windows. Same defect as #1988 on the normal getenv path. Audit callers.

On failing_ref, Windows `GetEnvironmentVariableW(..., nullptr, 0)` returning 0 is treated as unset. Empty `FOO=` and unset FOO JOIN. POSIX getenv already distinguishes NULL vs empty.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty user `proxy =` vs global. specimen-149 compose listed-without-equals vs image ENV. specimen-150 systemd `::` cwd search path.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
