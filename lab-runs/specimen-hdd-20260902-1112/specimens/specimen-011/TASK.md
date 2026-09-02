# TASK

A tiny build cache keys freshness by *input hash only*. First build writes `out.bin`. Second build asks for an extra output `out.sbom` from the same inputs. Cache reports FRESH. `out.sbom` does not exist.

The developer wants to know what identity the cache used and which requested outputs were outside that identity.
