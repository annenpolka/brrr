# TASK

A tiny build cache keys freshness by input hash only. First build writes `out.bin`
and also writes an empty `out.sbom` stub as a side effect of hashing (extra was
not requested). Second build asks for extra output `out.sbom` from the same
inputs. Cache reports FRESH. `out.sbom` exists. Its bytes are the empty stub.

The developer wants to know whether the extra file was produced for this request
or leftover from the identity write, and which requested outputs were outside
that identity.
