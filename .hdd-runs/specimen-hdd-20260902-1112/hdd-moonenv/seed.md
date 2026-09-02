CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

moon can keep the identity of a **previous task cache** after a `.env` file change should have been a different hash. `expand_env` loads env vars from the file but omits the env file from `task.inputs`. `get_file_hashes` then skips gitignored paths, so even an explicit `.env` input is omitted from the cache identity.

On failing_ref `5468dd6fb24ee98cbf6e4c05e3421e6a17e73199`:

```
// expand_env loads dotenv into self.env
// does not push env_file onto self.inputs

for file in files {
    if !self.is_file_ignored(file) {
        objects.push(file.clone());
    }
}
```

Public report (moonrepo/moon#481). Task lists `.env` as an input and `envFile: true`. Change `.env` FOO=123 → FOO=456; leftover cache is reused.

In-tree after the repair (not on failing_ref): `self.inputs.push(env_file)`; `get_file_hashes(files, allow_ignored=true)` for task inputs; test `tracks_input_changes_for_env_files`.

Case A — second `moon run` with unchanged `.env`:
  cache identity is current
  not leftover-after-env-change

Case B — `.env` contents flipped, leftover task cache:
  leftover: previous env file's task output
  env file omitted from inputs and/or skipped as gitignored
  cached output reused

Case C — delete the moon cache then run:
  fresh hash identity
  not leftover previous env

Case D — env file hashed as an input even if gitignored (post-repair shape, not on failing_ref):
  cache miss after `.env` change
  not leftover previous output

The developer wants to know which identity case B actually used for the task cache after the `.env` change: leftover previous-env output (env file omitted), current env-file identity, or omitted (no cache).

# OBSERVED

Public moonrepo/moon#481 (closed 2022-11-30). PR 482 squash `2959d6f0bcc9dbe12fb3f35e54186d245b44586a` (parent `5468dd6fb24ee98cbf6e4c05e3421e6a17e73199`). Local moon was not performed on this lab host.

Issue body: `.env` listed as an input does not break cache; leftover cached output is reused after the file changes.

On failing_ref, `expand_env` does not add `env_file` to `inputs`. `Git::get_file_hashes` skips `is_file_ignored`. `allow_ignored` is **not** on the failing revision. It is added by PR 482.

Not this packet: specimen-119 pixi leftover task cache filename omitting args. specimen-115 go-task leftover wildcard MATCH. turbo leftover env (no merged leftover-identity pair this run). specimen-133 stylelint leftover cache hashing empty CLI config.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
# crates/core/task/src/task.rs expand_env
# crates/core/vcs/src/git.rs get_file_hashes skips is_file_ignored

# public shape:
# leftover moon task cache after .env FOO=123 -> FOO=456
# env file omitted from inputs; gitignored paths skipped from hash
# cached output reused
```

Source-backed only. Do not execute untrusted checkouts on the host.

moonrepo/moon
  crates/core/task/src/task.rs
  crates/core/vcs/src/git.rs
  crates/core/runner/src/actions/run_target.rs
  crates/cli/tests/run_test.rs
  .env

RELEVANT MATERIAL

### expand_env_failing.rs

// Reduced excerpt of expand_env + get_file_hashes on failing_ref
// crates/core/task/src/task.rs expand_env
// crates/core/vcs/src/git.rs get_file_hashes
// 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
// env file loaded into env vars. Not pushed onto inputs.
// Gitignored paths omitted from hash objects.

    pub fn expand_env(&mut self, data: &ResolverData) -> Result<(), TaskError> {
        if let Some(env_file) = &self.options.env_file {
            let env_path = data.project_root.join(env_file);
            // no self.inputs.push(env_file)
            for entry in dotenvy::from_path_iter(&env_path).map_err(error_handler)? {
                let (key, value) = entry.map_err(error_handler)?;
                self.env.entry(key).or_insert(value);
            }
        }
        Ok(())
    }

    async fn get_file_hashes(&self, files: &[String]) -> VcsResult<BTreeMap<String, String>> {
        let mut objects = vec![];
        for file in files {
            if !self.is_file_ignored(file) {
                objects.push(file.clone());
            }
        }
        // hash-object --stdin-paths on objects only
    }

### leftover_identity_split.txt

Registry / fixture:
  moon.yml envFile: true, inputs include .env
  leftover task cache after FOO=123 -> FOO=456

Case A (second moon run, same .env):
  current cache identity
  not leftover-after-env-change

Case B (.env flipped, leftover cache):
  leftover: previous env file's task output
  env file omitted from inputs and/or skipped as gitignored
  cached output reused

Case C (delete moon cache):
  fresh hash identity
  not leftover previous env

Case D (env file hashed even if gitignored):
  cache miss after .env change
  not leftover previous output

Not this packet:
  pixi leftover task cache filename omitting args (specimen-119)
  go-task leftover wildcard MATCH (specimen-115)
  stylelint leftover cache hashing empty CLI config (specimen-133)

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
