# TASK

A struct flattens an externally tagged enum. One variant is a unit variant.

JSON `{"Unit":null}` deserializes into that struct. Serializing the resulting value fails.

The developer wants to know which direction of the format boundary accepted the unit variant, which direction rejected it, and what token sequence each side actually produced.
