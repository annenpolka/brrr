# identjson (reimpl)

origin.method: hdd
origin.trial: hdd-tfident
origin.kind: clean-room
parent: candidate-identjson
specimens: [specimen-081]

classification: USEFUL_COMPOSITION

## Primitive

Name the decode class of leftover identity JSON against a nil or present
identity schema: object, omitted/typed-null, or unsupported-attribute error.

## Why this might not exist

Printing IdentityJSON and Identity: nil still leaves “leftover bytes look
like identity; decode class is the miss” as a hand join.

## Core operation

Compile a record to JSON schema+state objects. Pass 1 is
`schema.Identity.ImpliedType()` (nil *Object is EmptyObject). Pass 2
unmarshals leftover IdentityJSON against that type. Extra keys are
unsupported-attribute. Absent JSON is omitted (nil schema) or typed-null
(present schema). rc=1 on decode error.

## Observable delta

One query names leftover `{"id":"foo"}` against Identity: nil as
unsupported-attribute, matching schema as object, omitted JSON as omitted,
and `arn` vs `id` as the same error class. Printing the two fields does not.

## Reality mapping

Owned records: `fixtures/081-nil-leftover.rec` (and the same facts as JSON)
error unsupported-attribute. `081-schema-present.rec` object.
`081-nil-json.rec` omitted. `081-mismatch.rec` error. Terraform is not
executed.

## Removed

Invented terraform Decode transcripts and live provider schema RPCs.

## Smallest artifact

Python 3 stdlib CLI `identjson` (schema+state objects + ImpliedType then
unmarshal, not a TSV key-list compare).
