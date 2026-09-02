# TASK

C++ JSON parsing of a `google.protobuf.Any` payload is given `ignore_unknown_fields = true`. The packed message JSON includes a field the compiled type does not know (`age` next to known `name`).

Golang and Python toolchains accept the document. C++ returns `Cannot find field.`

The developer wants to know which writer instance is parsing the inner Any object, which options that instance actually has, and why the outer ignore-unknown setting does not apply to the nested JSON object.
