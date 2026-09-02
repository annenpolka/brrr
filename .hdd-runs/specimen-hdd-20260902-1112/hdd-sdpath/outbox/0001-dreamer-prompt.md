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

systemd `get_paths_from_environ` can keep the identity of the **current working directory** as a unit search path after `SYSTEMD_UNIT_PATH` listed an empty `::` component and that listing should not have been a path. Unset, empty `""`, trailing `:`, and middle `::` are different identities. Empty components other than a trailing `:` are split into leftover `""` entries; `path_split_and_make_absolute` turns those into leftover cwd `.`.

On failing_ref `cad2c455ec1acff29a81421c58adbe0ffc191f65`:

```
static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":"); /* Whether to append the normal search paths after what's obtained
                                           from envvar */

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
}
```

`getenv` missing (`!e`) is unset. `e` pointing at `""` is empty-string. Trailing `:` means append built-in defaults. Middle `::` is not trailing-append. The FIXME is unenforced. Empty components become leftover cwd search-path identity.

Public PR (systemd/systemd#43355). Tests after the repair: unset → default search path; `""` → empty search path; `:` → same as unset (append defaults); `:foo` and `/foo::/bar` → EINVAL; trailing `/foo:` → `/foo` plus defaults.

In-tree after the repair (not on failing_ref): `path_is_valid_search_path` requires `isempty(path) || (isempty(startswith(path, ":")) && !strstr(path, "::"))`. Leading/middle empty is `-EINVAL`. Generator path parse errors propagate instead of becoming leftover empty generator paths.

Case A — `SYSTEMD_UNIT_PATH` unset:
  default search-path identity
  not leftover-cwd

Case B — `SYSTEMD_UNIT_PATH=/foo::/bar`, leftover empty component:
  leftover: cwd `.` as a search path
  empty `::` component split then made absolute
  same process lookup

Case C — `SYSTEMD_UNIT_PATH=""` (set, empty string):
  empty search path
  not leftover cwd; not default path

Case D — `SYSTEMD_UNIT_PATH=/foo:` (trailing colon):
  `/foo` plus built-in defaults
  not leftover cwd

Case E — leading/middle empty rejected (post-repair shape, not on failing_ref):
  EINVAL
  not leftover cwd search path

The developer wants to know which identity case B actually used for the unit search path after `::`: leftover cwd `.` (empty component made absolute), current listed directories only, empty search path, or omitted (defaults).

# OBSERVED

Public systemd/systemd#43355 (merged 2026-08-13). Squash `f4284e9cebac67ad7af3bc27b736cf1107b88127` (parent `cad2c455ec1acff29a81421c58adbe0ffc191f65`). Follow-up for `cf7d80a5fe549d4db11800015e02220dccec3096` (SYSTEMD_UNIT_PATH colon-separated prepend/append). Local systemd was not performed on this lab host.

PR title: path-lookup: reject empty env path components. Only trailing empty components have special meaning: they request appending the built-in defaults. Share validation between path lookup and systemd-analyze verify.

On failing_ref, `get_paths_from_environ` documents the FIXME and still splits empty components. Unset vs empty `""` vs `:` vs `::` are different getenv identities; empty components become leftover cwd.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty-override. compose leftover listed-without-equals vs image ENV (packed this tick as leftover empty-vs-unset environment, not PATH cwd).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref cad2c455ec1acff29a81421c58adbe0ffc191f65
# src/libsystemd/sd-path/path-lookup.c get_paths_from_environ

# public shape:
# leftover cwd search path after SYSTEMD_UNIT_PATH=/foo::/bar
# unset is default path; "" is empty path; trailing : appends defaults
# new process / EINVAL after repair does not keep leftover cwd
```

Source-backed only. Do not execute untrusted checkouts on the host.

systemd/systemd
  src/libsystemd/sd-path/path-lookup.c
  src/test/test-path-lookup.c
  src/analyze/analyze-verify-util.c

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  systemd get_paths_from_environ SYSTEMD_UNIT_PATH
  leftover cwd search path after empty :: component

Case A (unset SYSTEMD_UNIT_PATH):
  default search-path identity
  not leftover-cwd

Case B (/foo::/bar, leftover empty component):
  leftover: cwd . as a search path
  empty :: split then made absolute

Case C ("" empty string):
  empty search path
  not leftover cwd; not default path

Case D (/foo: trailing colon):
  /foo plus built-in defaults
  not leftover cwd

Case E (leading/middle empty rejected):
  EINVAL
  not leftover cwd search path

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  pip empty user proxy vs global (specimen-031)
  compose leftover listed-without-equals vs image ENV (this-tick compose packet)

### path_lookup_failing.c

/* Reduced excerpt of get_paths_from_environ on failing_ref
 * src/libsystemd/sd-path/path-lookup.c
 * cad2c455ec1acff29a81421c58adbe0ffc191f65
 * empty :: components are split then made absolute as leftover cwd.
 */

static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":");

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
}

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
