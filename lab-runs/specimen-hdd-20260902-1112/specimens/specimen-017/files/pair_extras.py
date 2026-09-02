
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
