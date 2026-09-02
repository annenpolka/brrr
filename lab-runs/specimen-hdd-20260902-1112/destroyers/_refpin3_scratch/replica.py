#!/usr/bin/env python3
"""Independent reconstruction of refpin inspect+format. Does not import refpin."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

IDENTITY_KEYS = ("rev", "narHash", "ref")
META_KEYS = ("lastModified", "revCount")
KNOWN = IDENTITY_KEYS + META_KEYS
NARHASH_MAX = 96
OMITTED = "-"

EXPECTED_LINE_RE = re.compile(
    r"expected:\s+(\S+)\s+\((no ref field|ref=([^)]*))\)",
    re.IGNORECASE,
)
GOT_LINE_RE = re.compile(
    r"got:\s+(\S+)\s+\((no ref field|ref=([^)]*))\)",
    re.IGNORECASE,
)
REV_BOTH_RE = re.compile(r"rev in both records:\s+(\S+)")
JSON_FIELD_STR_RE = re.compile(r'"(narHash|rev|ref)"\s*:\s*"([^"]*)"')
JSON_FIELD_NUM_RE = re.compile(r'"(lastModified|revCount)"\s*:\s*([0-9]+)')
NIX_MISMATCH_BLOBS_RE = re.compile(
    r"mismatch in field 'narHash' of input\s+'(\{.*?\})'\s*,\s*got\s+'(\{.*?\})'",
    re.DOTALL,
)


def parse_tsv(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError("expected key<TAB>value")
        parts = line.split("\t")
        if len(parts) != 2:
            raise ValueError("extra tab in value")
        key, rest = parts
        key = key.strip()
        value = rest.strip()
        if not key:
            raise ValueError("expected key<TAB>value")
        if key in seen:
            raise ValueError(f"duplicate field {key!r}")
        seen.add(key)
        if key in {"url", "type", "owner", "repo", "dir", "host", "path",
                   "submodules", "shallow", "allRefs", "name", "originalRef",
                   "id", "flake", "narHashAlgo", "inputs", "original", "locked",
                   "nodes", "root", "version"}:
            continue
        if key not in KNOWN:
            raise ValueError(f"unknown field {key!r}")
        fields[key] = value
    if "rev" not in fields or fields["rev"] == "":
        raise ValueError("missing rev")
    if "narHash" not in fields or fields["narHash"] == "":
        raise ValueError("missing narHash")
    return fields


def json_scalar(value: object) -> str:
    if isinstance(value, bool) or value is None:
        raise ValueError("not a lock scalar")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, str):
        return value
    raise ValueError("not a lock scalar")


def locked_from_mapping(obj: object) -> dict | None:
    if not isinstance(obj, dict):
        return None
    if "narHash" in obj and "rev" in obj:
        return obj
    locked = obj.get("locked")
    if isinstance(locked, dict) and "narHash" in locked and "rev" in locked:
        return locked
    return None


def locked_from_flake(obj: dict) -> dict:
    nodes = obj.get("nodes")
    if not isinstance(nodes, dict):
        raise ValueError("not a lock record")
    root = obj.get("root")
    found: list[tuple[str, dict]] = []
    for name, node in nodes.items():
        if name == root:
            continue
        locked = locked_from_mapping(node)
        if locked is not None:
            found.append((str(name), locked))
    if len(found) == 1:
        return found[0][1]
    if not found:
        root_node = nodes.get(root) if isinstance(root, str) else None
        locked = locked_from_mapping(root_node)
        if locked is not None:
            return locked
        raise ValueError("not a lock record")
    names = ", ".join(name for name, _ in found)
    raise ValueError(
        f"flake.lock has {len(found)} locked nodes ({names}); pass a single lock object"
    )


def record_from_locked(obj: dict) -> dict[str, str]:
    rev = obj.get("rev")
    nar_hash = obj.get("narHash")
    if rev is None or rev == "":
        raise ValueError("missing rev")
    if nar_hash is None or nar_hash == "":
        raise ValueError("missing narHash")
    fields: dict[str, str] = {
        "rev": json_scalar(rev),
        "narHash": json_scalar(nar_hash),
    }
    if not fields["rev"] or not fields["narHash"]:
        raise ValueError("missing rev" if not fields["rev"] else "missing narHash")
    for key in ("ref", "lastModified", "revCount"):
        if key in obj and obj[key] is not None:
            fields[key] = json_scalar(obj[key])
    return fields


def parse_json_value(data: object) -> dict[str, str] | tuple[dict[str, str], dict[str, str]]:
    if isinstance(data, list):
        if len(data) == 2:
            first = locked_from_mapping(data[0])
            second = locked_from_mapping(data[1])
            if first is None or second is None:
                raise ValueError("not a lock record")
            return record_from_locked(first), record_from_locked(second)
        if len(data) == 1:
            data = data[0]
        else:
            raise ValueError("not a lock record")
    if not isinstance(data, dict):
        raise ValueError("not a lock record")
    locked = locked_from_mapping(data)
    if locked is None and "nodes" in data:
        locked = locked_from_flake(data)
    if locked is None:
        raise ValueError("not a lock record")
    return record_from_locked(locked)


def parse_json_text(text: str) -> dict[str, str] | tuple[dict[str, str], dict[str, str]]:
    data = json.loads(text)
    return parse_json_value(data)


def is_mismatch_log(text: str) -> bool:
    if "mismatch in field 'narHash'" in text:
        return True
    if EXPECTED_LINE_RE.search(text) and GOT_LINE_RE.search(text):
        return True
    return False


def parse_mismatch(text: str) -> tuple[dict[str, str], dict[str, str]]:
    expected_fields: dict[str, str] = {}
    got_fields: dict[str, str] = {}
    blobs = NIX_MISMATCH_BLOBS_RE.search(text)
    if blobs:
        for match in JSON_FIELD_STR_RE.finditer(blobs.group(1)):
            expected_fields[match.group(1)] = match.group(2)
        for match in JSON_FIELD_NUM_RE.finditer(blobs.group(1)):
            expected_fields[match.group(1)] = match.group(2)
        for match in JSON_FIELD_STR_RE.finditer(blobs.group(2)):
            got_fields[match.group(1)] = match.group(2)
        for match in JSON_FIELD_NUM_RE.finditer(blobs.group(2)):
            got_fields[match.group(1)] = match.group(2)
    expected_line = EXPECTED_LINE_RE.search(text)
    got_line = GOT_LINE_RE.search(text)
    if expected_line:
        expected_fields["narHash"] = expected_line.group(1)
        kind = expected_line.group(2)
        if kind.lower() == "no ref field":
            expected_fields.pop("ref", None)
        else:
            expected_fields["ref"] = expected_line.group(3) or ""
    if got_line:
        got_fields["narHash"] = got_line.group(1)
        kind = got_line.group(2)
        if kind.lower() == "no ref field":
            got_fields.pop("ref", None)
        else:
            got_fields["ref"] = got_line.group(3) or ""
    rev_both = REV_BOTH_RE.search(text)
    if rev_both:
        expected_fields.setdefault("rev", rev_both.group(1))
        got_fields.setdefault("rev", rev_both.group(1))
    if "rev" not in expected_fields or "rev" not in got_fields:
        raise ValueError("missing rev")
    if "narHash" not in expected_fields or "narHash" not in got_fields:
        raise ValueError("missing narHash")
    return expected_fields, got_fields


def parse_one(text: str) -> dict[str, str]:
    text = text[1:] if text.startswith("\ufeff") else text
    stripped = text.lstrip()
    if not stripped.strip():
        raise ValueError("not a lock record")
    if is_mismatch_log(text):
        raise ValueError("mismatch log is a pair")
    if stripped.startswith("{") or stripped.startswith("["):
        parsed = parse_json_text(text)
        if isinstance(parsed, tuple):
            raise ValueError("json array of two lock objects is a pair")
        return parsed
    has_tsv = any(
        "\t" in line
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    if not has_tsv:
        raise ValueError("not a lock record")
    return parse_tsv(text)


def parse_pair(first_text: str, second_text: str | None) -> tuple[dict[str, str], dict[str, str]]:
    first_text = first_text[1:] if first_text.startswith("\ufeff") else first_text
    if second_text is None:
        stripped = first_text.lstrip()
        if is_mismatch_log(first_text):
            return parse_mismatch(first_text)
        if stripped.startswith("[") or stripped.startswith("{"):
            parsed = parse_json_text(first_text)
            if isinstance(parsed, tuple):
                return parsed
            raise ValueError("need SECOND")
        raise ValueError("need SECOND")
    if is_mismatch_log(first_text):
        raise ValueError("mismatch log is a pair")
    return parse_one(first_text), parse_one(second_text)


def present(rec: dict[str, str], key: str) -> bool:
    return key in rec


def value(rec: dict[str, str], key: str) -> str:
    return rec.get(key, "")


def ref_attached_of(first: dict[str, str], second: dict[str, str]) -> str:
    a = present(first, "ref")
    b = present(second, "ref")
    if not a and b:
        return "attached"
    if a and not b:
        return "ref_removed"
    if a and b and first["ref"] != second["ref"]:
        return "both-disagree"
    if a and b:
        return "both"
    return "none"


def classify_key(first: dict[str, str], second: dict[str, str], key: str) -> str:
    a = present(first, key)
    b = present(second, key)
    if not a and not b:
        return "absent"
    if a and not b:
        return "present-only-a"
    if b and not a:
        return "present-only-b"
    if first[key] == second[key]:
        return "equal"
    return "value-diverged"


def verdict_of(*, same_rev: bool, identity_changed: bool, attached: str,
               meta_value: list[str], meta_presence: list[str]) -> str:
    if not same_rev:
        return "rev-diverged"
    if identity_changed and attached == "attached":
        return "pinned-rev-default-ref-changed-hash"
    if identity_changed and attached == "ref_removed":
        return "pinned-rev-default-ref-removed-hash"
    if identity_changed and attached == "none":
        return "hash-changed-no-ref"
    if attached == "both-disagree":
        return "both-disagree"
    if identity_changed and attached == "both":
        return "both-same-ref-changed-hash"
    if attached == "attached":
        return "ref-attached-same-hash"
    if attached == "ref_removed":
        return "ref-removed-same-hash"
    if meta_presence:
        return "metadata-presence"
    if meta_value:
        return "lastModified-only"
    return "identical"


def inspect(first: dict[str, str], second: dict[str, str]) -> dict:
    same_rev = first["rev"] == second["rev"]
    identity_changed = first["narHash"] != second["narHash"]
    attached = ref_attached_of(first, second)
    equal: list[str] = []
    diverged: list[str] = []
    present_only_a: list[str] = []
    present_only_b: list[str] = []
    for key in KNOWN:
        kind = classify_key(first, second, key)
        if kind == "equal":
            equal.append(key)
        elif kind == "value-diverged":
            diverged.append(key)
        elif kind == "present-only-a":
            present_only_a.append(key)
        elif kind == "present-only-b":
            present_only_b.append(key)
    meta_value = [key for key in META_KEYS if key in diverged]
    meta_presence = [
        key for key in META_KEYS if key in present_only_a or key in present_only_b
    ]
    verdict = verdict_of(
        same_rev=same_rev,
        identity_changed=identity_changed,
        attached=attached,
        meta_value=meta_value,
        meta_presence=meta_presence,
    )
    attached_ref = second.get("ref", "") if attached == "attached" else ""
    removed_ref = first.get("ref", "") if attached == "ref_removed" else ""
    return {
        "first": first,
        "second": second,
        "same_rev": same_rev,
        "identity_changed": identity_changed,
        "ref_attached": attached,
        "verdict": verdict,
        "equal": equal,
        "diverged": diverged,
        "present_only_a": present_only_a,
        "present_only_b": present_only_b,
        "attached_ref": attached_ref,
        "removed_ref": removed_ref,
    }


def exit_status(verdict: str) -> int:
    if verdict in {"identical", "lastModified-only", "metadata-presence"}:
        return 0
    return 1


def cap_hash(value: str) -> tuple[str, bool]:
    if len(value) > NARHASH_MAX:
        return value[:NARHASH_MAX] + "…", True
    return value, False


def fmt_list(items: list[str]) -> str:
    return "\t".join(items) if items else OMITTED


def format_report(result: dict) -> str:
    first = result["first"]
    second = result["second"]
    hash_a, cap_a = cap_hash(first["narHash"])
    hash_b, cap_b = cap_hash(second["narHash"])
    lines = [
        "time_axis\tFIRST=earlier SECOND=later",
        f"verdict\t{result['verdict']}",
        f"same_rev\t{'yes' if result['same_rev'] else 'no'}",
        f"rev_a\t{first['rev']}",
        f"rev_b\t{second['rev']}",
    ]
    if result["same_rev"]:
        lines.insert(2, f"rev\t{first['rev']}")
    lines.extend(
        [
            f"narHash_a\t{hash_a}",
            f"narHash_b\t{hash_b}",
            f"identity_changed\t{'yes' if result['identity_changed'] else 'no'}",
            f"ref_present_a\t{'yes' if present(first, 'ref') else 'no'}",
            f"ref_present_b\t{'yes' if present(second, 'ref') else 'no'}",
            f"ref_a\t{first.get('ref', OMITTED) if present(first, 'ref') else OMITTED}",
            f"ref_b\t{second.get('ref', OMITTED) if present(second, 'ref') else OMITTED}",
            f"ref_attached\t{result['ref_attached']}",
            f"attached_ref\t{result['attached_ref'] or OMITTED}",
            f"removed_ref\t{result['removed_ref'] or OMITTED}",
            f"equal\t{fmt_list(result['equal'])}",
            f"diverged\t{fmt_list(result['diverged'])}",
            f"present_only_a\t{fmt_list(result['present_only_a'])}",
            f"present_only_b\t{fmt_list(result['present_only_b'])}",
            f"source_a\tREPLICA",
            f"source_b\tREPLICA",
        ]
    )
    if cap_a or cap_b:
        lines.append("narHash_capped\tyes")
    return "\n".join(lines) + "\n"


def thin_harvest(first: dict[str, str], second: dict[str, str]) -> dict[str, str]:
    """Caller-labeled rows only: same rev, one-sided ref on SECOND, narHash string !=."""
    same_rev = first["rev"] == second["rev"]
    identity_changed = first["narHash"] != second["narHash"]
    attached = (not present(first, "ref")) and present(second, "ref")
    removed = present(first, "ref") and (not present(second, "ref"))
    harvest = same_rev and identity_changed and attached
    return {
        "same_rev": "yes" if same_rev else "no",
        "identity_changed": "yes" if identity_changed else "no",
        "ref_attached": (
            "attached" if attached else ("ref_removed" if removed else "other")
        ),
        "harvest": "yes" if harvest else "no",
        "attached_ref": second.get("ref", "-") if attached else "-",
    }


def load_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("replica: need FIRST", file=sys.stderr)
        return 2
    first_text = load_text(args[0])
    second_text = load_text(args[1]) if len(args) > 1 else None
    first, second = parse_pair(first_text, second_text)
    result = inspect(first, second)
    sys.stdout.write(format_report(result))
    return exit_status(result["verdict"])


if __name__ == "__main__":
    raise SystemExit(main())
