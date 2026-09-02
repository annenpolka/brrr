ACCEPT_R1

contrastiveness: high (unchanged schema vs leftover watch client after append vs non-watch generate vs reload in loop)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — watcher path and schema object are different identities; leftover schemaContext stayed current after schema.prisma changed
ecosystem: prisma / generate watch
mechanism_family: leftover-generated-client, omitted-schema-reload, watch-schemacontext-reuse

Packet is the failing world only. Do not assume a root cause.
