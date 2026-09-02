# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Name a field whose optionality tags disagree with identity markers.

## Nearest existing operation

Read struct tags (`grep omitempty`, `grep listMapKey`, `grep +optional`).

## Observable delta

One query joining `json omitempty` / `+optional` with `+listMapKey`. Grep hits
both tags without naming which identity key is optional.

## Reality mapping

Owned Go / comment-tag fixture. A list field carries `// +listMapKey=NAME`.
The element type has a field whose json name is `NAME` and whose json tag
includes `omitempty` (and maybe `// +optional`). That field is optional in
tags and required identity for the list-map. No CRD generator. No cluster.

Specimen-052 excerpt: `HostAlias.IP` (`json:"ip,omitempty"`, listMapKey=ip)
and `LocalObjectReference.Name` (`json:"name,omitempty"` plus `+optional`,
listMapKey=name).

## Research boundary

Does not run code-generator, controller-gen, or kubectl. Does not emit
OpenAPI or repair CRDs. Parses owned struct tags only.

## Removed

k8s-field-analyzer, live codegen, apiserver admission.

## Smallest artifact

Python 3 stdlib CLI `tagjoin`.

## Why existing tools are not enough

`grep omitempty` and `grep listMapKey` both hit. The join — this json name
is a list-map key *and* omitempty — is still a hand comparison, including
when the key lives on the element type rather than the list field.
