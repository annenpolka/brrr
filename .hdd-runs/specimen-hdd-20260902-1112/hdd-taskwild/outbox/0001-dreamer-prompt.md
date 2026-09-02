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

Task's checksum fingerprint can keep the identity of a **wildcard template** after two different MATCH instantiations should be different tasks. `.task/checksum/<name>` is keyed by the template name (`build-*`), so leftover checksum from `build-foo` is reused as up-to-date for `build-bar`.

On failing_ref `1e2121a99f6414e3bf4565e5736a116bef10be91`, compiled tasks keep `Task: origTask.Task` (the pattern). `Name()` / `LocalName()` do not include MATCH. `fingerprint.IsTaskUpToDate` uses that name as the cache key. Wildcard parameter is omitted from fingerprint identity.

Public report (go-task/task#1795): automatically concat the wildcard parameter on the cache key. Discussion #1794: two wildcard instantiations share one checksum.

In-tree after the repair (not on failing_ref): `FullName` replaces `*` with MATCH; `Name()` / `LocalName()` use FullName; testdata `build-*` writes `.task/checksum/build-wildcard`.

Case A — first `task build-foo` (checksum method):
  checksum written for the template name
  not leftover yet

Case B — later `task build-bar` with leftover checksum from foo:
  leftover: up-to-date identity of foo
  MATCH bar omitted from the key

Case C — non-wildcard `build` with its own checksum file:
  unique key
  not this leftover

Case D — delete `.task/checksum` then run bar:
  fresh identity
  not leftover fingerprint

The developer wants to know which identity case B actually left in `.task/checksum/`: leftover foo checksum reused as bar, separate bar checksum, or omitted (no checksum file).

# OBSERVED

Public go-task/task#1795 (closed 2025-09-11). PR 1808 squash `48039be12cdfc6b6871dbe9f1d6977027d660889` (parent `1e2121a99f6414e3bf4565e5736a116bef10be91`). Local task was not performed on this lab host.

Issue: wildcard parameter is not on the fingerprint cache key. Two MATCH instantiations share leftover checksum identity.

On failing_ref, compiledTask copies origTask.Task as the name. MATCH is a var, not the checksum key. FullName is **not** on the failing revision. It is added by PR 1808 (`fullName` replaces `*` with MATCH; `Name()` prefers FullName).

Not this packet: specimen-076/088/104 (gradle compiler fingerprints). pants leftover fingerprint (job-0464 hunt: no leftover-identity merged pair). cargo leftover (091/099/101).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 1e2121a99f6414e3bf4565e5736a116bef10be91
# variables.go compiledTask / taskfile/ast/task.go Name

# public shape:
# leftover .task/checksum/build-* from build-foo
# task build-bar reports up-to-date
```

Source-backed only. Do not execute untrusted checkouts on the host.

go-task/task
  variables.go
  taskfile/ast/task.go
  testdata/checksum/Taskfile.yml

RELEVANT MATERIAL

### compiled_task_name_failing.go

// Reduced excerpt of compiledTask / Name on failing_ref
// variables.go / taskfile/ast/task.go
// 1e2121a99f6414e3bf4565e5736a116bef10be91
// Task name is the template. MATCH is not the checksum key.

	new := ast.Task{
		Task: origTask.Task,
		// no FullName
	}

func (t *Task) Name() string {
	if t.Label != "" {
		return t.Label
	}
	return t.Task
}

### leftover_identity_split.txt

Registry / fixture:
  tasks:
    build-*:
      method: checksum
  leftover .task/checksum from build-foo

Case A (first build-foo):
  checksum written for template name
  not leftover yet

Case B (later build-bar, leftover foo checksum):
  leftover: up-to-date identity of foo
  MATCH bar omitted

Case C (non-wildcard build):
  unique key
  not this leftover

Case D (delete .task/checksum):
  fresh identity
  not leftover fingerprint

Not this packet:
  gradle compiler fingerprints (specimen-076/088/104)
  pants leftover fingerprint (no merged pair)

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
