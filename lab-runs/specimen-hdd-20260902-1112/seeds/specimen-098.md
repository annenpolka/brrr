CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

pip's resolvelib factory can treat a **link requirement that also names an extra** as a different identity from a constraint (or second request) on the same package without extras. Installing `pkg-1.0-py2.py3-none-any.whl[ext]` together with `pkg==1` (or an indirect `pkg2` that depends on `pkg1[ext]==1.0` plus an explicit `pkg1-1.0.whl[ext]` path) can fail to share the link candidate.

On failing_ref `a15dd75d98884c94a77d349b800c7c755d8c34e4`, `_make_candidate_from_link` builds a base `LinkCandidate` then, if extras are set, wraps it with `_make_extras_candidate`. `_make_requirements_from_install_req` for a path/link ireq with extras passes `extras=frozenset(ireq.extras)` into that function, so the **base** link candidate is not required separately. Constraints iterate `constraint.links` with `extras=frozenset()`.

Case A — path wheel without extras plus `pkg==1`:
  one link candidate, no extra wrap
  install succeeds
  no leftover extra identity

Case B — path wheel **with** extras plus a version constraint on the same name (`{wheel}[ext]` and `pkg==1`):
  failing_ref: extras candidate is not the same object the constraint looks up as the base link
  public: pip install local with extra fails dependency resolution (#12372)

Case C — two path wheels, `pkg2` depends on `pkg1[ext]==1.0`, plus explicit `{wheel_one}[ext]`:
  same leftover: extra on the explicit link is not applied on top of a shared base candidate
  in-tree after the repair: `test_new_resolver_constraint_on_link_with_extra_indirect`

Case D — extras only via specifier (`pkg[ext]==1.0`) with an index, no explicit link:
  not this leftover (no link candidate cache keyed without extras)

The developer wants to know which identity the factory stored for the explicit path: leftover extras-wrapped candidate that the constraint cannot reuse, a base link plus a second extras requirement, or omitted.

# OBSERVED

Public pypa/pip#12372 / PR 12392 (sanderr; merged 2023-12-17, merge `417ca92b439dba33d707b5da2493358863256bc3`). Failing world pinned on merge first parent `a15dd75d98884c94a77d349b800c7c755d8c34e4`. Local pip execution was not performed on this lab host.

PR body: extras handling where constraints on a package are not compatible with an explicit link candidate that also has an extra.

On failing_ref, `_make_candidate_from_link` returns `_make_extras_candidate(base, extras)` when extras are non-empty. `_make_requirements_from_install_req` for a link ireq passes those extras into that call, so only the extras-wrapped candidate is yielded. `find_candidates` for a later constraint/base request does not see that wrapped object as the explicit link base.

In-tree tests added on the PR (`test_new_resolver_constraint_on_link_with_extra`, `test_new_resolver_constraint_on_link_with_extra_indirect`) are **not** on the failing revision.

Not this packet: specimen-031 (pip empty extra). specimen-080 (owned extra marker fixture). pipmark (hdd-pipmark). `--require-hashes` extras #9644 / PR 9995. extras-on-error-message #13618 (unmerged #13659).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref a15dd75d98884c94a77d349b800c7c755d8c34e4
# src/pip/_internal/resolution/resolvelib/factory.py
# _make_candidate_from_link / _make_requirements_from_install_req

# public shape:
# pip install --no-index path/to/pkg-1.0-py2.py3-none-any.whl[ext] pkg==1
```

Source-backed only. Do not execute untrusted checkouts on the host.

pypa/pip
  src/pip/_internal/resolution/resolvelib/factory.py
  tests/functional/test_new_resolver.py

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  explicit path wheel pkg-1.0-py2.py3-none-any.whl
  extra name ext
  constraint pkg==1

Case A (path without extras + pkg==1):
  base link candidate
  no extras wrap
  install ok

Case B (path with extras + pkg==1):
  failing_ref extras-wrapped candidate
  constraint looks up base link with extras empty
  leftover: wrap is not the base

Case C (pkg2 depends pkg1[ext]==1.0 plus explicit pkg1.whl[ext]):
  same leftover on the explicit extra link

Case D (pkg[ext]==1.0 from index, no path link):
  not this leftover

Not this packet:
  pip empty extra (specimen-031)
  extra marker fixture (specimen-080)
  pipmark
  require-hashes extras (#9644)

### make_candidate_from_link_failing.py

# Reduced excerpt of _make_candidate_from_link on failing_ref
# src/pip/_internal/resolution/resolvelib/factory.py
# a15dd75d98884c94a77d349b800c7c755d8c34e4
# If extras are set, the returned candidate is the extras wrap, not the base link.

            base = self._link_candidate_cache[link]

        if not extras:
            return base
        return self._make_extras_candidate(base, extras, comes_from=template)

### make_requirements_failing.py

# Reduced excerpt of _make_requirements_from_install_req on failing_ref
# Link ireq passes extras into _make_candidate_from_link, so only the wrap is yielded.

            cand = self._make_candidate_from_link(
                ireq.link,
                extras=frozenset(ireq.extras),
                template=ireq,
                name=canonicalize_name(ireq.name) if ireq.name else None,
                version=None,
            )

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
