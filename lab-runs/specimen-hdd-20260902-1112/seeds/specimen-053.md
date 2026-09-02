CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Two specs run in parallel (`turbo_tests`). Both call `with_git_configured`, which writes git credentials to a store file under the working directory.

CI (`common`) fails with:

```
expected: "***private.com\n"
     got: "***github.com\n"
```

`.gitconfig` already used a per-run random suffix. The credential store path did not.

The developer wants to know which file the two processes actually shared, and why one spec could read the other spec's credentials.

# OBSERVED

Public dependabot/dependabot-core PR 14944. Failing world around `Dependabot::SharedHelpers.with_git_configured`.

On the failing revision, `configure_git_to_use_https_with_credentials` registers:

```
git config --global credential.helper '!... --file #{Dir.pwd}/git.store'
```

and writes credentials to that single path. Parallel examples `shared_helpers_spec.rb` and `file_fetchers/base_spec.rb` both enter `with_git_configured`, so one process can read `git.store` bytes written by the other.

The global gitconfig path already used `SecureRandom.hex(16)` under a temp dir (`#{suffix}.gitconfig`). The credential store stayed `Dir.pwd/git.store`.

This packet does not include a local clone; treat the snippets and CI message as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# CI job name reported on the PR: common
# turbo_tests running:
#   common/spec/dependabot/shared_helpers_spec.rb
#   common/spec/dependabot/file_fetchers/base_spec.rb
bundle exec rspec common/spec/dependabot/shared_helpers_spec.rb
```

Not executed on this lab host.

dependabot/dependabot-core
  common/lib/dependabot/shared_helpers.rb
  common/spec/dependabot/shared_helpers_spec.rb

RELEVANT MATERIAL

### git_store_failing.rb

# Reduced excerpt of failing with_git_configured (not a full checkout).
# gitconfig path is unique; credential store path is not.

git_config_global_path = File.expand_path("#{SecureRandom.hex(16)}.gitconfig", tmp)
# credential helper file:
#   #{Dir.pwd}/git.store

run_shell_command(
  "git config --global credential.helper "   "'!#{credential_helper_path} --file #{Dir.pwd}/git.store'"
)

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
