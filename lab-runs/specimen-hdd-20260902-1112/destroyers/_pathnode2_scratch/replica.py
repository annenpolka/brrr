#!/usr/bin/env python3
"""Independent reconstruction of pathnode TSV join. Does not import pathnode."""
from __future__ import annotations


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def parse_found(token: str) -> bool:
    value = token.strip().lower()
    if value in {"found", "yes", "true"}:
        return True
    if value in {"missing", "miss", "no", "false"}:
        return False
    raise ValueError(f"lookup result must be found|missing, got {token!r}")


def parse_record(text: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str, bool]]]:
    collects: list[tuple[str, str]] = []
    registers: list[tuple[str, str]] = []
    lookups: list[tuple[str, str, bool]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError("expected key<TAB>value")
        key, rest = line.split("\t", 1)
        key = key.strip()
        parts = [p for p in rest.split("\t") if p != ""]
        if key not in {"collect", "register", "lookup"}:
            raise ValueError(f"unknown field {key!r}")
        if key == "collect":
            if len(parts) < 2:
                raise ValueError("collect needs path, node")
            collects.append((parts[0], parts[1]))
        elif key == "register":
            if len(parts) < 2:
                raise ValueError("register needs fixture, node")
            registers.append((parts[0], parts[1]))
        elif key == "lookup":
            if len(parts) < 3:
                raise ValueError("lookup needs fixture, node, found|missing")
            lookups.append((parts[0], parts[1], parse_found(parts[2])))
    if not collects:
        raise ValueError("missing collect")
    return collects, registers, lookups


def format_report(text: str) -> str:
    collects, registers, lookups = parse_record(text)
    by_path: dict[str, list[str]] = {}
    for path, node in collects:
        by_path.setdefault(path, []).append(node)
    dups = []
    for path, nodes in by_path.items():
        if len(nodes) < 2:
            continue
        uniq = unique(nodes)
        dups.append((path, uniq, len(uniq) == 1))
    bound: dict[str, list[str]] = {}
    for fixture, node in registers:
        bound.setdefault(fixture, [])
        if node not in bound[fixture]:
            bound[fixture].append(node)
    by_node: dict[str, list[str]] = {}
    for path, node in collects:
        by_node.setdefault(node, []).append(path)
    shared = []
    for node, paths in by_node.items():
        uniq = unique(paths)
        if len(uniq) < 2:
            continue
        shared.append((node, uniq))
    misses = []
    for fixture, node, found in lookups:
        bound_nodes = list(bound.get(fixture) or [])
        unbound = node not in bound_nodes
        if found and not unbound:
            continue
        misses.append((fixture, node, bound_nodes, found, unbound))
    lines = [
        "paths\t" + "\t".join(p for p, _ in collects),
        "nodes\t" + "\t".join(n for _, n in collects),
    ]
    if dups:
        for path, nodes, same in dups:
            lines.append(
                "dup_path\t" + path + "\tnodes\t" + "\t".join(nodes) + "\tsame_node\t" + ("yes" if same else "no")
            )
    else:
        lines.append("dup_path\tnone")
    if shared:
        for node, paths in shared:
            lines.append("shared_node\t" + node + "\tpaths\t" + "\t".join(paths))
    else:
        lines.append("shared_node\tnone")
    if misses:
        for fixture, node, bound_nodes, found, unbound in misses:
            bound_s = "\t".join(bound_nodes) if bound_nodes else "none"
            lines.append(
                "miss\t"
                + fixture
                + "\tlookup\t"
                + node
                + "\tbound_to\t"
                + bound_s
                + "\tfound\t"
                + ("yes" if found else "no")
                + "\tunbound\t"
                + ("yes" if unbound else "no")
            )
    else:
        lines.append("miss\tnone")
    return "\n".join(lines) + "\n"
