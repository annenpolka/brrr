# TASK

uv's lock can keep the identity of a **previous extra-gated package version as unconditional** after a later extra activation should have been a different lock object. `simplify_conflict_markers` treats extras-known-to-be-enabled inferences as always-true, so an extras conflict marker is omitted (simplified to `true`) from `uv.lock`.

On failing_ref `2bda549bcca67f06df602901ad9cdf30d35add00`, `simplify_conflict_markers` walks every edge and, if all inference sets satisfy the conflict marker, calls `assume_conflict_item` / `assume_not_conflict_item`. Ambiguous edges (two outgoing edges with the same package name, e.g. sympy 1.13.1 and sympy 1.13.3) are **not** skipped.

Public report (astral-sh/uv#11479). `uv sync -p 3.12` installs only `torch==2.5.1`. `uv sync -p 3.12 --extra m3gnet` installs both `torch==2.2.0` and leftover `torch==2.5.1`, plus two sympy versions. Lock excerpt for always-required `e3nn`:

```
[[package]]
name = "e3nn"
dependencies = [
    { name = "sympy", version = "1.13.1", source = { registry = "https://pypi.org/simple" } },
    { name = "sympy", version = "1.13.3", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.2.0", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.5.1", source = { registry = "https://pypi.org/simple" } },
]
```

The extras marker for sympy 1.13.1 / torch 2.5.1 was simplified to true. Those versions are leftover unconditional identity.

In-tree after the repair (not on failing_ref): skip simplification when `ambiguous_edges > 1`; test `duplicate_torch_and_sympy_because_of_wrong_inferences`.

Case A — `uv sync` with no extras (production only):
  torch 2.5.1 is the production identity
  not leftover extras-marker identity

Case B — `uv sync --extra m3gnet` with leftover lock that omitted extras markers:
  leftover: torch 2.5.1 / sympy 1.13.1 as unconditional
  extras marker omitted from lock identity
  also installs torch 2.2.0 / sympy 1.13.3 (extra-gated)

Case C — lock written with extras markers kept (post-repair shape, not on failing_ref):
  extra-gated versions stay extra-gated
  not leftover unconditional identity

Case D — delete `uv.lock` then `uv lock` with extras declared as conflicts:
  fresh lock identity
  not leftover simplified-to-true markers

The developer wants to know which identity case B actually left in `uv.lock` for e3nn→torch 2.5.1: leftover unconditional (extras marker omitted), extra-gated marker for m3gnet, or omitted (no torch 2.5.1 edge).
