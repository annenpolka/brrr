# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A package extra `bar` is gated by an environment marker that is false on this interpreter (`python_version < "3"` on 3.14). Install still materializes the extra.

The developer wants to know whether the extra was installed even though its marker failed, and which extra should have been skipped.

# OBSERVED

Owned files/marker_extra.py. Host-executed:

extra bar
marker_ok False
installed True
should_skip True
wrongly_installed True

# COMMANDS

python3 files/marker_extra.py

TREE

files/marker_extra.py

RELEVANT MATERIAL

### marker_extra.py

#!/usr/bin/env python3
"""Owned analog: extra install ignores environment marker."""
def extra_wanted(extra, marker_ok):
    # failing: extra always installed
    return True

def extra_wanted_fixed(extra, marker_ok):
    return bool(marker_ok)

def main():
    extra = "bar"
    marker_ok = False  # python_version < "3" on 3.14
    installed = extra_wanted(extra, marker_ok)
    print("extra", extra)
    print("marker_ok", marker_ok)
    print("installed", installed)
    print("should_skip", not marker_ok)
    print("wrongly_installed", installed and not marker_ok)

if __name__ == "__main__":
    main()

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
