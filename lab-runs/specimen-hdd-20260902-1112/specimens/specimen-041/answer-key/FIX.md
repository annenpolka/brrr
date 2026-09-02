KNOWN FIX (sealed): protocolbuffers/protobuf#5099 merge 37b5617d42d02d225faa1d64565696f5bfb8e61a.

AnyWriter::StartAny built the nested ProtoStreamObjectWriter with the four-argument TypeInfo constructor, which stores Options::Defaults() and never calls set_ignore_unknown_fields from the parent. Unknown JSON keys inside Any therefore errored even when the caller set ignore_unknown_fields on the outer parse.

Repair: add a TypeInfo constructor that takes Options, copy ignore_unknown_fields / use_lower_camel_for_enums, and pass parent_->options_ at the AnyWriter allocation.

Regression: JsonUtilTest.TestParsingUnknownAnyFields — default parse fails on unknown_field inside Any; with ignore_unknown_fields the known string_value still unpacks.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
