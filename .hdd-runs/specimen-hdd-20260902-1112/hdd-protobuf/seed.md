CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

C++ JSON parsing of a `google.protobuf.Any` payload is given `ignore_unknown_fields = true`. The packed message JSON includes a field the compiled type does not know (`age` next to known `name`).

Golang and Python toolchains accept the document. C++ returns `Cannot find field.`

The developer wants to know which writer instance is parsing the inner Any object, which options that instance actually has, and why the outer ignore-unknown setting does not apply to the nested JSON object.

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

# COMMANDS

```
git checkout d340bdf50821e6db173a9e41bc7bde740275ba33
# C++ JSON util tests (full protobuf build; not run in this packet)
bazel test //src/google/protobuf/util:json_util_test
```

The issue JSON plus the writer excerpt are the world. Do not claim local execution evidence.

protocolbuffers/protobuf @ d340bdf50821e6db173a9e41bc7bde740275ba33
  src/google/protobuf/util/internal/protostream_objectwriter.h
  src/google/protobuf/util/internal/protostream_objectwriter.cc
  src/google/protobuf/util/json_util_test.cc
  src/google/protobuf/any.proto

RELEVANT MATERIAL

### src/google/protobuf/util/internal/protostream_objectwriter.cc.excerpt

// excerpt @ d340bdf50821e6db173a9e41bc7bde740275ba33
// src/google/protobuf/util/internal/protostream_objectwriter.cc

ProtoStreamObjectWriter::ProtoStreamObjectWriter(
    TypeResolver* type_resolver, const google::protobuf::Type& type,
    strings::ByteSink* output, ErrorListener* listener,
    const ProtoStreamObjectWriter::Options& options)
    : ProtoWriter(type_resolver, type, output, listener),
      master_type_(type),
      current_(nullptr),
      options_(options) {
  set_ignore_unknown_fields(options_.ignore_unknown_fields);
  set_use_lower_camel_for_enums(options_.use_lower_camel_for_enums);
}

ProtoStreamObjectWriter::ProtoStreamObjectWriter(
    const TypeInfo* typeinfo, const google::protobuf::Type& type,
    strings::ByteSink* output, ErrorListener* listener)
    : ProtoWriter(typeinfo, type, output, listener),
      master_type_(type),
      current_(nullptr),
      options_(ProtoStreamObjectWriter::Options::Defaults()) {}

void ProtoStreamObjectWriter::AnyWriter::StartAny(const DataPiece& value) {
  // ... resolve type_url_ ...
  ow_.reset(new ProtoStreamObjectWriter(parent_->typeinfo(), *type, &output_,
                                        parent_->listener()));
  if (!is_well_known_type_) {
    ow_->StartObject("");
  }
  for (int i = 0; i < uninterpreted_events_.size(); ++i) {
    uninterpreted_events_[i].Replay(this);
  }
}

### src/google/protobuf/util/internal/protostream_objectwriter.h.excerpt

// excerpt @ d340bdf50821e6db173a9e41bc7bde740275ba33
// src/google/protobuf/util/internal/protostream_objectwriter.h

  struct Options {
    bool struct_integers_as_strings;
    // Not treat unknown fields as an error. If there is an unknown fields,
    // just ignore it and continue to process the rest.
    bool ignore_unknown_fields;
    bool use_lower_camel_for_enums;
    bool ignore_null_value_map_entry;
    Options()
        : struct_integers_as_strings(false),
          ignore_unknown_fields(false),
          use_lower_camel_for_enums(false),
          ignore_null_value_map_entry(false) {}
    static const Options& Defaults() {
      static Options defaults;
      return defaults;
    }
  };

  // public constructor: Options default to Defaults()
  ProtoStreamObjectWriter(TypeResolver* type_resolver,
                          const google::protobuf::Type& type,
                          strings::ByteSink* output, ErrorListener* listener,
                          const ProtoStreamObjectWriter::Options& options =
                              ProtoStreamObjectWriter::Options::Defaults());

  // private TypeInfo constructor: no Options parameter
  ProtoStreamObjectWriter(const TypeInfo* typeinfo,
                          const google::protobuf::Type& type,
                          strings::ByteSink* output, ErrorListener* listener);

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
