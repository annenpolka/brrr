# OBSERVED

Public issue protocolbuffers/protobuf#5086 on C++ protobuf v3.5.0+, checkout around merge parent `d340bdf50821e6db173a9e41bc7bde740275ba33`.

Message shape:

```
syntax = "proto3";
package example;
import "google/protobuf/any.proto";
message Child { string name = 1; }
message Parent { google.protobuf.Any child = 1; }
```

JSON:

```json
{
  "child": {
    "@type": "example.Child",
    "name": "Jane Doe",
    "age": 42
  }
}
```

With `ignore_unknown_fields` true on the C++ JSON load, the call still fails: `Cannot find field.`

On this revision, the TypeResolver constructor copies options onto the writer (`set_ignore_unknown_fields(options_.ignore_unknown_fields)`). The TypeInfo constructor used when starting an Any does not take Options and initializes `options_(ProtoStreamObjectWriter::Options::Defaults())`. `AnyWriter::StartAny` constructs the nested writer with that TypeInfo constructor.
