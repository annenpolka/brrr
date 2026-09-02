CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Outer parser ignore_unknown=true. Nested Any-like payload is parsed by an inner instance whose options default ignore_unknown=false. Unknown field errors on the inner instance.

The developer wants to know which instance ran and whether the outer flag applied.

# OBSERVED

Owned option records (no protobuf):

outer ignore_unknown=true
inner ignore_unknown=false
inner_error Cannot find field.
outer_options_applied_inner false

# COMMANDS

See nestedopt CLI.

options only

RELEVANT MATERIAL

### options.txt

outer.ignore_unknown=true
inner.ignore_unknown=false

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
