#!/usr/bin/env python3
"""Host-executed destroyer attacks against tagjoin. Not a test suite."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CLI = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin"
)
FX = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/fixtures"
)
S052 = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-052"
)
OUT = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_tagjoin2_scratch"
)


def run(name: str, args: list[str], stdin: str | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )
    (OUT / f"{name}.out").write_text(proc.stdout, encoding="utf-8")
    (OUT / f"{name}.err").write_text(proc.stderr, encoding="utf-8")
    (OUT / f"{name}.rc").write_text(str(proc.returncode), encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def show(name: str, rc: int, stdout: str, stderr: str) -> None:
    print(f"\n===== {name} rc={rc} =====")
    sys.stdout.write(stdout)
    if stderr:
        print("--- STDERR ---")
        sys.stdout.write(stderr)
    print(f"===== end {name} =====")


CASES: list[tuple[str, list[str], str | None]] = []


def add(name: str, args: list[str], stdin: str | None = None) -> None:
    CASES.append((name, args, stdin))


add("owned052", [str(FX / "052-types.go")])
add("owned052_check", ["--check", str(FX / "052-types.go")])
add("excerpt052", [str(S052 / "files/types_excerpt.go")])
add("apply052", [str(S052 / "files/apply_error.txt")])
add("empty_json_name", [str(FX / "empty-json-name.go")])
add(
    "empty_json_stdin",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:",omitempty"`
}
""",
)
add("wrong_wire", [str(FX / "wrong-wire.go")])
add(
    "go_name_address",
    ["-"],
    """type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"address,omitempty"`
}
""",
)
add(
    "casefold_IP_ip",
    ["-"],
    """type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "casefold_ip_IP",
    ["-"],
    """type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"IP,omitempty"`
}
""",
)
add(
    "sibling_owns_ip",
    ["-"],
    """type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"address,omitempty"`
	Addr string `json:"ip,omitempty"`
}
""",
)
add(
    "listmap_ip_json_address",
    ["-"],
    """type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"address,omitempty"`
}
""",
)
add(
    "json_dash",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"-"`
}
""",
)
add(
    "json_dash_Name",
    ["-"],
    """type Spec struct {
	// +listMapKey=Name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"-"`
}
""",
)
add(
    "no_json_tag_Name",
    ["-"],
    """type Spec struct {
	// +listMapKey=Name
	Items []Item `json:"items"`
}
type Item struct {
	Name string
}
""",
)
add(
    "no_json_tag_name",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string
}
""",
)
add(
    "dup_json_names",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	A string `json:"name,omitempty"`
	B string `json:"name"`
}
""",
)
add("dup_type", [str(FX / "dup-type.go")])
add("dup_listmapkey", [str(FX / "dup-listmapkey.go")])
add(
    "dup_listmapkey_comma",
    ["-"],
    """type Spec struct {
	// +listMapKey=name,port
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name,omitempty"`
	Port int `json:"port"`
}
""",
)
add("yaml_crd", [str(FX / "crd-list-map.yaml")])
add(
    "yaml_required",
    ["-"],
    """ports:
  type: array
  x-kubernetes-list-map-keys:
  - containerPort
  items:
    required:
    - containerPort
    properties:
      containerPort:
        type: integer
""",
)
add(
    "yaml_default",
    ["-"],
    """hostAliases:
  type: array
  x-kubernetes-list-map-keys:
  - ip
  items:
    properties:
      ip:
        type: string
        default: ""
""",
)
add(
    "yaml_ref",
    ["-"],
    """hostAliases:
  type: array
  x-kubernetes-list-map-keys:
  - ip
  items:
    $ref: '#/definitions/HostAlias'
definitions:
  HostAlias:
    required:
    - ip
    properties:
      ip:
        type: string
""",
)
add(
    "yaml_flow_keys",
    ["-"],
    """hostAliases:
  type: array
  x-kubernetes-list-map-keys: [ip]
  items:
    properties:
      ip:
        type: string
""",
)
add(
    "yaml_hyphen_key",
    ["-"],
    """volumeMounts:
  type: array
  x-kubernetes-list-map-keys:
  - mount-path
  items:
    properties:
      mount-path:
        type: string
""",
)
add(
    "json_crd",
    ["-"],
    """{
  "hostAliases": {
    "type": "array",
    "x-kubernetes-list-map-keys": ["ip"],
    "items": {
      "properties": {
        "ip": {"type": "string"}
      }
    }
  }
}
""",
)
add(
    "full_crd_shape",
    ["-"],
    """apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
spec:
  versions:
  - name: v1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              hostAliases:
                type: array
                x-kubernetes-list-map-keys:
                - ip
                x-kubernetes-list-type: map
                items:
                  type: object
                  properties:
                    ip:
                      type: string
                    hostnames:
                      type: array
                      items:
                        type: string
              imagePullSecrets:
                type: array
                x-kubernetes-list-map-keys:
                - name
                items:
                  type: object
                  properties:
                    name:
                      type: string
""",
)
add(
    "plus_default",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	// +default=""
	Name string `json:"name,omitempty"`
}
""",
)
add(
    "plus_default_check",
    ["--check", "-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	// +default=""
	Name string `json:"name,omitempty"`
}
""",
)
add("bom", [str(FX / "bom.go")])
add("spaces_eq", [str(FX / "spaces-eq.go")])
add("embed_inline", [str(FX / "embed-inline.go")])
add("untagged_list", [str(FX / "untagged-list.go")])
add("agree_name", [str(FX / "agree-name.go")])
add("agree_name_check", ["--check", str(FX / "agree-name.go")])
add("unseen_ports", [str(FX / "unseen-ports.go")])
add(
    "identity_shaped_text",
    ["-"],
    "the apiserver rejected x-kubernetes-list-map-keys without required or default\n",
)
add(
    "identity_shaped_listmapkey_text",
    ["-"],
    "docs say use +listMapKey=ip on the list field when the key is optional\n",
)
add(
    "join_none_empty",
    ["-"],
    "package p\n",
)
add(
    "block_comment",
    ["-"],
    """type Spec struct {
	/* +listMapKey=ip */
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "patch_merge_only",
    ["-"],
    """type Spec struct {
	// +patchMergeKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "listmapkey_on_type",
    ["-"],
    """// +listMapKey=ip
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
type Spec struct {
	HostAliases []HostAlias `json:"hostAliases"`
}
""",
)
add(
    "protobuf_opt_required_json",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name" protobuf:"bytes,1,opt,name=name"`
}
""",
)
add(
    "omitzero",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name,omitzero"`
}
""",
)
add(
    "kubebuilder_optional",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	// +kubebuilder:validation:Optional
	Name string `json:"name"`
}
""",
)
add(
    "json_inline_named",
    ["-"],
    """type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	Inner Base `json:"inner,inline"`
}
type Base struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "json_inline_empty_name",
    ["-"],
    """type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	Inner Base `json:",inline"`
}
type Base struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "go_yaml_same_blob",
    [str(FX / "052-types.go"), str(FX / "crd-list-map.yaml")],
)
add(
    "check_collision",
    ["--check", str(FX / "dup-type.go")],
)
add(
    "check_missing",
    ["--check", str(FX / "wrong-wire.go")],
)
add(
    "check_allow_missing",
    ["--check", "--allow-missing", str(FX / "wrong-wire.go")],
)
add(
    "two_files_split",
    [],  # filled below via tmp files
)
add(
    "star_slice",
    ["-"],
    """type Spec struct {
	// +listMapKey=ip
	HostAliases *[]HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "type_alias",
    ["-"],
    """type Alias HostAlias
type Spec struct {
	// +listMapKey=ip
	HostAliases []Alias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "anon_struct",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []struct {
		Name string `json:"name,omitempty"`
	} `json:"items"`
}
""",
)
add(
    "generics",
    ["-"],
    """type Spec[T any] struct {
	// +listMapKey=name
	Items []T `json:"items"`
}
type Item struct {
	Name string `json:"name,omitempty"`
}
""",
)
add(
    "listmapkey_on_elem_field",
    ["-"],
    """type Item struct {
	// +listMapKey=name
	Name string `json:"name,omitempty"`
}
""",
)
add(
    "var_clears_markers",
    ["-"],
    """type Spec struct {
	// +listMapKey=ip
	var ignored = 1
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
)
add(
    "same_line_marker",
    ["-"],
    """type Spec struct {
	Items []Item `json:"items"` // +listMapKey=name
}
type Item struct {
	Name string `json:"name,omitempty"`
}
""",
)
add(
    "yaml_anchors",
    ["-"],
    """defs: &ha
  type: array
  x-kubernetes-list-map-keys:
  - ip
  items:
    properties:
      ip:
        type: string
hostAliases: *ha
""",
)
add(
    "observed_crd_fragment",
    ["-"],
    """imagePullSecrets:
  items:
    properties:
      name:
        description: Name of the referent. ...
        type: string
    type: object
    x-kubernetes-map-type: atomic
  type: array
  x-kubernetes-list-map-keys:
  - name
  x-kubernetes-list-type: map
""",
)
add(
    "yaml_required_wrong_level",
    ["-"],
    """hostAliases:
  type: array
  required:
  - ip
  x-kubernetes-list-map-keys:
  - ip
  items:
    properties:
      ip:
        type: string
""",
)
add(
    "optional_no_omitempty",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	// +optional
	Name string `json:"name"`
}
""",
)
add(
    "json_name_tab",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"na\tme,omitempty"`
}
""",
)
add(
    "listmapkey_empty_eq",
    ["-"],
    """type Spec struct {
	// +listMapKey=
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name,omitempty"`
}
""",
)
add(
    "unparsed_plus_garbage_yaml",
    ["-"],
    "x-kubernetes-list-map-keys: [this is : not: valid: yaml: [[\n",
)
add(
    "dev_null",
    ["/dev/null"],
)
add(
    "missing_file",
    ["/no/such/tagjoin.go"],
)
add(
    "directory",
    [str(FX)],
)
add(
    "multi_agree_ports",
    [str(FX / "agree-name.go"), str(FX / "unseen-ports.go")],
)
add(
    "check_identity_text",
    ["--check", "-"],
    "the apiserver rejected x-kubernetes-list-map-keys without required or default\n",
)
add(
    "json_omitempty_listmapkey_omitempty",
    ["-"],
    """type Spec struct {
	// +listMapKey=omitempty
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:",omitempty"`
}
""",
)
add(
    "two_case_json_collision",
    ["-"],
    """type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	A string `json:"name,omitempty"`
	B string `json:"Name"`
}
""",
)
add(
    "folded_only_collision",
    ["-"],
    """type Spec struct {
	// +listMapKey=NAME
	Items []Item `json:"items"`
}
type Item struct {
	A string `json:"name,omitempty"`
	B string `json:"Name"`
}
""",
)


def main() -> None:
    # split-file package: list in a.go, elem in b.go
    a = OUT / "split_list.go"
    b = OUT / "split_elem.go"
    a.write_text(
        """package v1
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
""",
        encoding="utf-8",
    )
    b.write_text(
        """package v1
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
        encoding="utf-8",
    )
    CASES.append(("split_files", [str(a), str(b)], None))
    CASES.append(("split_files_reversed", [str(b), str(a)], None))

    summary = []
    for name, args, stdin in CASES:
        rc, stdout, stderr = run(name, args, stdin)
        show(name, rc, stdout, stderr)
        first = stdout.splitlines()[0] if stdout.splitlines() else ""
        summary.append(f"{name}\trc={rc}\t{first}")
    (OUT / "SUMMARY.tsv").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n##### SUMMARY #####")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
