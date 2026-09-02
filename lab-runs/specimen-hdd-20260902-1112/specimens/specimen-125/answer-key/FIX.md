KNOWN FIX (sealed): astral-sh/uv PR 11513 commit 91593d42d990397695a15750dcb8453c62a71b7d.

failing_ref is series parent 2bda549bcca67f06df602901ad9cdf30d35add00.

simplify_conflict_markers applied extras inferences to ambiguous same-name edges and omitted extras markers (simplified to true), so leftover unconditional torch/sympy identity stayed in uv.lock after extra activation.

PR repair: skip conflict-marker simplification when ambiguous_edges > 1 (two outgoing edges with the same package name).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
