# identjson (clean-room reimpl)

Name the decode class of leftover identity JSON against a nil or present
identity schema.

This copy compiles records to JSON schema+state objects, then drives a
two-pass decode: ImpliedType (nil *Object is EmptyObject), then unmarshal.
Extra attributes are the unsupported-attribute error. rc=1 on decode error.

```
identjson RECORD
identjson < RECORD
```

RECORD is a TSV table (`schema` / `identity_json` rows) or a JSON document
(`schema` + `state`).
