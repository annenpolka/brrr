# OBSERVED

Public astral-sh/uv#11479 (closed 2025-02-18). PR 11513 rebase tip `91593d42d990397695a15750dcb8453c62a71b7d` (series parent `2bda549bcca67f06df602901ad9cdf30d35add00`). Local uv was not performed on this lab host.

Issue body: `uv sync --extra m3gnet` installs two torch versions and two sympy versions because some e3nn edges have extras conflict markers simplified to true.

On failing_ref, `simplify_conflict_markers` does not skip ambiguous same-name edges. `assume_conflict_item` can drop the extras marker from lock identity. The skip for `ambiguous_edges > 1` is **not** on the failing revision. It is added by PR 11513.

Not this packet: extraedge / specimen-080 / specimen-098 extras CLI. specimen-006 (uv CI cache leftover fingerprints). specimen-102 (uv leftover git vs directory in lock). specimen-106 (pdm extra path URL expanded). specimen-123/124 earthly leftover CACHE --id unexpanded ARG.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
