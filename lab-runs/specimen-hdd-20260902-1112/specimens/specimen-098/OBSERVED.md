# OBSERVED

Public pypa/pip#12372 / PR 12392 (sanderr; merged 2023-12-17, merge `417ca92b439dba33d707b5da2493358863256bc3`). Failing world pinned on merge first parent `a15dd75d98884c94a77d349b800c7c755d8c34e4`. Local pip execution was not performed on this lab host.

PR body: extras handling where constraints on a package are not compatible with an explicit link candidate that also has an extra.

On failing_ref, `_make_candidate_from_link` returns `_make_extras_candidate(base, extras)` when extras are non-empty. `_make_requirements_from_install_req` for a link ireq passes those extras into that call, so only the extras-wrapped candidate is yielded. `find_candidates` for a later constraint/base request does not see that wrapped object as the explicit link base.

In-tree tests added on the PR (`test_new_resolver_constraint_on_link_with_extra`, `test_new_resolver_constraint_on_link_with_extra_indirect`) are **not** on the failing revision.

Not this packet: specimen-031 (pip empty extra). specimen-080 (owned extra marker fixture). pipmark (hdd-pipmark). `--require-hashes` extras #9644 / PR 9995. extras-on-error-message #13618 (unmerged #13659).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
