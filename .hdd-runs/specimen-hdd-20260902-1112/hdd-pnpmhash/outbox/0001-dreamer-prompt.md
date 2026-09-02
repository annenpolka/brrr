# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A pnpm lockfile's `patchedDependencies` entry for a selector can be either an object `{ path, hash }` or a bare hash string.

Case A — lockfile v9 / pre-simplify (object):

```
patchedDependencies:
  express@4.18.1:
    path: patches/express@4.18.1.patch
    hash: 4eb8b160deadbeef
```

A reader that takes `entry.hash` gets `4eb8b160deadbeef`. A reader that treats the entry as a string gets nothing useful.

Case B — pnpm 11+ simplified lockfile (selector → hash string):

```
patchedDependencies:
  express@4.18.1: 4eb8b160deadbeef
```

A reader that still does `entry.hash` / `originalPatchFile?.hash` on a string gets **empty**. Frozen install then fails with `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH` because the current patchedDependencies configuration does not match the value found in the lockfile.

Case C — selector present with empty string hash:

```
patchedDependencies:
  express@4.18.1: ""
```

Case D — selector missing from `patchedDependencies` while a `patches/` file still exists.

The developer wants to know which identity the lockfile actually contained for `express@4.18.1`: path+hash object, hash-only string, empty hash, or omitted.

# OBSERVED

Public pnpm/pnpm#10911 (merged): lockfile `patchedDependencies` simplified from `Record<string, { path: string, hash: string }>` to `Record<string, string>` (selector → hash). Patch file paths come from user config (`opts.patchedDependencies`), not from the lockfile.

Downstream (0x80/isolate-package#201 / #202): `@pnpm/lockfile-file` passes the field through unchanged, so a pnpm 11 lockfile yields bare hash strings instead of `{ path, hash }` objects. `copyPatches` only read `originalPatchFile?.hash`, which is undefined for a string entry, so the isolated lockfile wrote an **empty** hash. pnpm then rejected frozen install: `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH`.

This packet is an owned two-shape fixture of those identities. It does not include a local pnpm checkout. Do not execute untrusted checkouts on the host. Not specimen-068 (Unix node env-hop).

# COMMANDS

```
# not executed on this lab host
# pnpm 10 object vs pnpm 11 string (PR 10911)

# case A object
# patchedDependencies.express@4.18.1.hash is 4eb8b160deadbeef
# patchedDependencies.express@4.18.1.path is patches/express@4.18.1.patch

# case B string
# patchedDependencies.express@4.18.1 is 4eb8b160deadbeef
# originalPatchFile?.hash is empty

# case C empty string
# case D omitted selector
```

Owned fixtures in `files/` are the two identities, not a pnpm run.

local-fixture
  files/patcheddeps.object.yaml
  files/patcheddeps.hash.yaml

RELEVANT MATERIAL

### patcheddeps.hash.yaml

patchedDependencies:
  express@4.18.1: fixture-patch-hash

### patcheddeps.object.yaml

patchedDependencies:
  express@4.18.1:
    path: patches/express@4.18.1.patch
    hash: fixture-patch-hash

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
