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
