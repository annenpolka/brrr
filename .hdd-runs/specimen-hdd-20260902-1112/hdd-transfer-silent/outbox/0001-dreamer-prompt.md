# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Paired completions of the same extra request `A[foo]`. Extra map is identical: `foo → B`. Pair A’s package object still lists `B` in `requires`. Pair B’s package object has an empty `requires` list. One pair’s extra dependency is in the resolved set; the other pair’s is not.

The developer wants one question that names that difference without reading both traces by hand.

# OBSERVED

Owned fixture files/pair_extras.py. Pair A PASS / pair B FAIL. Same extras map, same requested extra. Only observed difference: whether `requires` still contains the extra’s dependency.

Grounded in the same extra-request mismatch family as python-poetry/poetry#10314: extras map lists B, one object still has B in requires, the other does not.

## Captured host execution (stdlib, no third-party packages)
```
pair_A_fresh_requires recognized ['B'] resolved_extra_deps ['B'] PASS
pair_B_pruned_requires recognized ['B'] resolved_extra_deps [] FAIL
only_axis requires_contains_extra_dep
request A[foo]
```

# COMMANDS

```
python3 files/pair_extras.py
```

files/pair_extras.py

RELEVANT MATERIAL

### pair_extras.py


#!/usr/bin/env python3
def complete(requires, extras, requested_extras):
    recognized = []
    for extra in requested_extras:
        recognized.extend(extras.get(extra, []))
    from_requires = [dep for dep in requires if dep in recognized]
    return recognized, from_requires

def main() -> None:
    extras = {"foo": ["B"]}
    requested = ["foo"]
    rec_a, got_a = complete(["B"], extras, requested)
    rec_b, got_b = complete([], extras, requested)
    def label(got):
        return "PASS" if got == ["B"] else "FAIL"
    print("pair_A_fresh_requires recognized", rec_a, "resolved_extra_deps", got_a, label(got_a))
    print("pair_B_pruned_requires recognized", rec_b, "resolved_extra_deps", got_b, label(got_b))
    print("only_axis requires_contains_extra_dep")
    print("request A[foo]")

if __name__ == "__main__":
    main()

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
