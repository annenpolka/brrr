# TASK

A cache record is printed as JSON. The record contains a hex `key`, an `inputs` object, and an `outputs` list that includes `out.sbom`. A second build requests `out.sbom` and prints FRESH. `out.sbom` does not exist.

The developer wants to know whether those listed output names participated in freshness, or only sat next to the identity in the dump.
