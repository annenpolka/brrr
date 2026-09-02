# OBSERVED

Public dependabot/dependabot-core PR 14944. Failing world around `Dependabot::SharedHelpers.with_git_configured`.

On the failing revision, `configure_git_to_use_https_with_credentials` registers:

```
git config --global credential.helper '!... --file #{Dir.pwd}/git.store'
```

and writes credentials to that single path. Parallel examples `shared_helpers_spec.rb` and `file_fetchers/base_spec.rb` both enter `with_git_configured`, so one process can read `git.store` bytes written by the other.

The global gitconfig path already used `SecureRandom.hex(16)` under a temp dir (`#{suffix}.gitconfig`). The credential store stayed `Dir.pwd/git.store`.

This packet does not include a local clone; treat the snippets and CI message as the world. Do not execute untrusted checkouts on the host.
