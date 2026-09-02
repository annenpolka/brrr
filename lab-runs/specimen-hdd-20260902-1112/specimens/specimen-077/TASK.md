# TASK

Two encodings of the same record `{flag: false, name: x}`. Encoder A omits `flag` because it is false. Encoder B includes `"flag": false`. Downstream treats missing key as true.

The developer wants to know which encoder dropped the false and whether the decoded object still has the key.
