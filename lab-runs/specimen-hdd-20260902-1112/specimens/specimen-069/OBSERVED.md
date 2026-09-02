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
