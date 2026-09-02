# COMMANDS

```
# in-tree on failing_ref aed61af66c5b16f40d45a573be9ebdea7cce2b36
# (not executed on this lab host)

go test ./internal/terraform -run 'TestContext2Plan_resource_identity_refresh$' -count=1
# "identity type mismatch": failed to decode identity: unsupported attribute "arn"...
# "no previous identity": identity {id: "foo"} after refresh-only plan

# Decode leftover identity JSON against a schema with Identity == nil
# State:
#   AttrsJSON: {"id":"foo","foo":"bar"}
#   IdentityJSON: {"id": "foo"}
#   IdentitySchemaVersion: 0
# Schema:
#   Body: aws_instance id/foo
#   Identity: nil
# Decode takes the IdentityJSON != nil branch and calls schema.Identity.ImpliedType()
```

Not executed on this lab host.
