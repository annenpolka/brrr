KNOWN FIX (sealed): protocolbuffers/protobuf#15983 merge f00528d90a3bd1d21d86b83ff9c530040a5b53eb.

Scheduled staleness used a shell OR so a failing Bazel staleness target still produced step success via a following print. Repair: emit the regenerate hint, then invoke the tagged tests with no OR-true, so the workflow step exit code is the test exit code.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
