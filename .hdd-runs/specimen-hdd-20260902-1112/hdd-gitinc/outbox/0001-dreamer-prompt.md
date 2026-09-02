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

`actions/checkout` v7 on a self-hosted Windows runner writes `includeIf.gitdir:...path` entries pointing at a temp credentials config:

```
includeIf.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
```

Post-job cleanup runs the equivalent of:

```
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
```

Git prints:

```
error: invalid pattern: C:\runner\_work\_temp\git-credentials-.config
```

The workflow can still conclude successfully. A later checkout on the same worktree sees the leftover `includeIf` and repeats the error.

The developer wants to know which git config *value* cleanup tried to match, whether that value was treated as a regex, and which `includeIf` entries remained.

# OBSERVED

Public actions/checkout#2528 / PR 2530. Failing world in `src/git-command-manager.ts` `tryConfigUnsetValue`.

On the failing revision:

```
args.push('--unset', configKey, configValue)
const output = await this.execGit(args, true)
return output.exitCode === 0
```

Git's `git config --unset <name> <value-pattern>` treats the third argument as a regular expression. Native Windows paths contain `\`. `\` is an invalid regex escape here, so git reports `error: invalid pattern` and does not remove the entry.

`tryConfigUnsetValue` passes `true` as the allow-failure flag to `execGit`, so a nonzero git exit becomes a boolean false rather than a thrown failure. Cleanup continues.

Sibling helper `tryConfigUnset` uses `--unset-all` with only the key (no value pattern).

v5.0.1 on the same runner does not take this v7 credential-layout cleanup path; no invalid-pattern message and no leftover includeIf.

This packet does not include a local clone; treat the snippets and git error as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
# error: invalid pattern: C:\runner\_work\_temp\git-credentials-.config
git config --local --get-regexp includeif
```

Not executed on this lab host.

actions/checkout
  src/git-command-manager.ts
  dist/index.js

RELEVANT MATERIAL

### cleanup_error.txt

git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
error: invalid pattern: C:\runner\_work\_temp\git-credentials-.config

### tryConfigUnsetValue_failing.ts

// Reduced excerpt on failing_ref
// src/git-command-manager.ts

async tryConfigUnsetValue(
  configKey: string,
  configValue: string,
  globalConfig?: boolean,
  configFile?: string
): Promise<boolean> {
  const args = ['config']
  if (configFile) {
    args.push('--file', configFile)
  } else {
    args.push(globalConfig ? '--global' : '--local')
  }
  args.push('--unset', configKey, configValue)
  const output = await this.execGit(args, true)
  return output.exitCode === 0
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
