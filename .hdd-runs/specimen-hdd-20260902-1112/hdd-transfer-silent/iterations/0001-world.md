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
