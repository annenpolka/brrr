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
