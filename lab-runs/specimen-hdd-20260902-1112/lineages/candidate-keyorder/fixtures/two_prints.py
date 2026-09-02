#!/usr/bin/env python3
"""Owned fixture: two prints of {1: 0, 0: 0} — sorted keys vs insertion."""

OBJ = {1: 0, 0: 0}


def print_sorted(mapping: dict) -> str:
    inner = ", ".join(f"{k!r}: {mapping[k]!r}" for k in sorted(mapping))
    return "{" + inner + "}"


def print_insertion(mapping: dict) -> str:
    inner = ", ".join(f"{k!r}: {mapping[k]!r}" for k in mapping)
    return "{" + inner + "}"


if __name__ == "__main__":
    print(print_sorted(OBJ))
    print(print_insertion(OBJ))
