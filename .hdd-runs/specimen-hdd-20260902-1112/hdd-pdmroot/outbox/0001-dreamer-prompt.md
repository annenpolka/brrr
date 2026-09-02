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

`pdm lock --update-reuse` of a project that names a **local path extra** can rewrite that extra's lock identity from a portable `${PROJECT_ROOT}` URL to a **machine-absolute `file:///` URL**, even when the lock `path` field stays relative.

Public report (pdm-project/pdm#2852). Monorepo:

```
my-repo/
  app/   pyproject + pdm.lock   depends on "lib[test] @ file:///${PROJECT_ROOT}/../lib"
  lib/   pyproject
```

On failing_ref `cc17967ace76ff2fdf455106a6eb26da50685260`, first `pdm lock` writes:

```
[[package]]
name = "lib"
version = "0.1.0"
extras = ["test"]
path = "../lib"
dependencies = [
    "lib @ file:///${PROJECT_ROOT}/../lib",
    "pytest",
]
```

Immediately afterwards, `pdm lock --update-reuse` rewrites the extra line to an expanded absolute URL:

```
    "lib @ file:///mnt/c/pdm-minimal/lib",
```

`format_lockfile` only attempted `relative_to(project.root)` when `FileRequirement.path` was already absolute. Extra-require handling mutated the shared `install_requires` list (`self._data.install_requires` without a copy), so a later reuse pass saw a different URL identity than the first lock.

Case A — no extras, only a path dep `lib @ file:///${PROJECT_ROOT}/../lib`:
  `--update-reuse` keeps the variable URL
  no leftover expansion

Case B — extra `lib[test]` path dep, `pdm lock` then `pdm lock --update-reuse`:
  first lock: portable `${PROJECT_ROOT}` URL + relative `path`
  failing_ref reuse: leftover absolute `file:///...` URL next to the same relative `path`
  leftover identity: expanded URL vs portable PROJECT_ROOT URL

Case C — extra deps that are registry names (pytest), not path:
  no file URL to expand
  not this leftover

Case D — `pdm lock` without `--update-reuse` after a clean tree:
  first-write identity only
  not the reuse leftover

The developer wants to know which identity case B actually stored for the extra path dep after `--update-reuse`: leftover expanded absolute URL, the portable `${PROJECT_ROOT}` URL, or omitted.

# OBSERVED

Public pdm-project/pdm#2852 closed 2024-05-08. PR 2874 merge `931de2106b37e8dc55efb84de6bf7a704ad28842` (parent `cc17967ace76ff2fdf455106a6eb26da50685260`). Title: keep `${PROJECT_ROOT}` after `pdm lock --update-reuse`. Local PDM execution was not performed on this lab host.

On failing_ref, `format_lockfile` (src/pdm/cli/utils.py):

```
if isinstance(r, FileRequirement) and r.path and r.path.is_absolute():
    try:
        r.path = Path(os.path.normpath(r.path)).relative_to(os.path.normpath(project.root))
        r.url = backend.relative_path_to_url(r.path.as_posix())
    except ValueError:
        pass
```

Relative `path = "../lib"` skipped the rewrite. Extra-require assembly used `result = self._data.install_requires` (same list object) then appended extras, so reuse could emit an expanded URL while `path` stayed relative.

News file `news/2852.bugfix.md` is **absent** on `cc17967ace76ff2fdf455106a6eb26da50685260`. It is added by PR 2874.

Not this packet: specimen-006/022/023/102 (uv git vs directory source kinds / Poetry path inside git checkout). specimen-021 (poetry extras). specimen-031/098 (pip extras-on-link).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref cc17967ace76ff2fdf455106a6eb26da50685260
# src/pdm/cli/utils.py format_lockfile FileRequirement branch
# src/pdm/models/setup.py extras_require vs install_requires

# public shape:
# pdm lock
#   path = "../lib"
#   "lib @ file:///${PROJECT_ROOT}/../lib"
# pdm lock --update-reuse
#   path = "../lib"
#   failing: "lib @ file:///mnt/c/pdm-minimal/lib"
```

Source-backed only. Do not execute untrusted checkouts on the host.

pdm-project/pdm
  src/pdm/cli/utils.py
  src/pdm/models/setup.py
  news/2852.bugfix.md

RELEVANT MATERIAL

### format_lockfile_failing.py

# Reduced excerpt of format_lockfile on failing_ref
# cc17967ace76ff2fdf455106a6eb26da50685260
# URL rewrite runs only when path is already absolute.

        deps: list[str] = []
        for r in fetched_dependencies[v.dep_key]:
            if isinstance(r, FileRequirement) and r.path and r.path.is_absolute():
                try:
                    r.path = Path(os.path.normpath(r.path)).relative_to(os.path.normpath(project.root))
                    r.url = backend.relative_path_to_url(r.path.as_posix())
                except ValueError:
                    pass
            deps.append(r.as_line())

### leftover_identity_split.txt

Registry / fixture:
  app depends on lib[test] @ file:///${PROJECT_ROOT}/../lib
  lib is a sibling path package

Case A (path dep, no extras):
  --update-reuse keeps ${PROJECT_ROOT}
  no leftover expansion

Case B (extra lib[test], lock then --update-reuse):
  first lock: file:///${PROJECT_ROOT}/../lib + path ../lib
  failing reuse: file:///mnt/c/pdm-minimal/lib + path ../lib
  leftover: expanded URL vs portable PROJECT_ROOT URL

Case C (registry extra pytest):
  no file URL
  not this leftover

Case D (first pdm lock only):
  first-write identity
  not reuse leftover

Not this packet:
  uv git vs directory (specimen-006/022/023/102)
  pip extras-on-link (specimen-098)

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
