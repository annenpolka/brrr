#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet specimen-053 (dependabot parallel git.store race)."""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from paths import SPECIMENS
from update_index import main as update_index


packet = dict(
    id="specimen-053",
    manifest="""
id: specimen-053
kind: REAL_SOURCE_BACKED
repository: dependabot/dependabot-core
failing_ref: 7deeefef423e5defe996f7ab3ad1a63a7041a981
fixed_ref: ac2cd9a751975ecead87fa2a636ecdc212fc7276
source_pr: https://github.com/dependabot/dependabot-core/pull/14944
mechanism_tags:
  - race-test
  - shared-temp-path
  - parallel-ci
ecosystem: ruby
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 6500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

Two specs run in parallel (`turbo_tests`). Both call `with_git_configured`, which writes git credentials to a store file under the working directory.

CI (`common`) fails with:

```
expected: "***private.com\\n"
     got: "***github.com\\n"
```

`.gitconfig` already used a per-run random suffix. The credential store path did not.

The developer wants to know which file the two processes actually shared, and why one spec could read the other spec's credentials.
""",
    observed="""# OBSERVED

Public dependabot/dependabot-core PR 14944. Failing world around `Dependabot::SharedHelpers.with_git_configured`.

On the failing revision, `configure_git_to_use_https_with_credentials` registers:

```
git config --global credential.helper '!... --file #{Dir.pwd}/git.store'
```

and writes credentials to that single path. Parallel examples `shared_helpers_spec.rb` and `file_fetchers/base_spec.rb` both enter `with_git_configured`, so one process can read `git.store` bytes written by the other.

The global gitconfig path already used `SecureRandom.hex(16)` under a temp dir (`#{suffix}.gitconfig`). The credential store stayed `Dir.pwd/git.store`.

This packet does not include a local clone; treat the snippets and CI message as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
# CI job name reported on the PR: common
# turbo_tests running:
#   common/spec/dependabot/shared_helpers_spec.rb
#   common/spec/dependabot/file_fetchers/base_spec.rb
bundle exec rspec common/spec/dependabot/shared_helpers_spec.rb
```

Not executed on this lab host.
""",
    tree="""dependabot/dependabot-core
  common/lib/dependabot/shared_helpers.rb
  common/spec/dependabot/shared_helpers_spec.rb
""",
    source="""repository: dependabot/dependabot-core
pr: https://github.com/dependabot/dependabot-core/pull/14944
failing_ref (merge first parent): 7deeefef423e5defe996f7ab3ad1a63a7041a981
fixed_ref (merge commit): ac2cd9a751975ecead87fa2a636ecdc212fc7276
head_sha: b6f21a98454e6aeb8e610e56888ec08ac56517f0
merged_at: 2026-05-15
merged_by: brettfo
changed_files: common/lib/dependabot/shared_helpers.rb, common/spec/dependabot/shared_helpers_spec.rb
""",
    answer_key="""KNOWN FIX (sealed): dependabot/dependabot-core PR 14944 merge ac2cd9a751975ecead87fa2a636ecdc212fc7276.

with_git_configured already uniquified the global gitconfig filename. The credential store stayed Dir.pwd/git.store, so turbo_tests workers clobbered each other's credentials.

Repair: one random_suffix for both #{suffix}.gitconfig and Dir.pwd/#{suffix}.git.store; pass git_store_path into configure_git_to_use_https_with_credentials; rm_f the store in ensure. Specs assert the unique .git.store name and cleanup.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (unique gitconfig vs shared git.store; CI expected private.com vs got github.com)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — parallel workers leaked credentials through a leftover shared path after a sibling file was already uniquified
ecosystem: ruby
mechanism_family: race-test, shared-temp-path, parallel-ci

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "git_store_failing.rb": '''# Reduced excerpt of failing with_git_configured (not a full checkout).
# gitconfig path is unique; credential store path is not.

git_config_global_path = File.expand_path("#{SecureRandom.hex(16)}.gitconfig", tmp)
# credential helper file:
#   #{Dir.pwd}/git.store

run_shell_command(
  "git config --global credential.helper " \
  "'!#{credential_helper_path} --file #{Dir.pwd}/git.store'"
)
'''
    },
)

if __name__ == "__main__":
    dest = emit(packet)
    seed = write_seed(SPECIMENS / "specimen-053")
    print(dest)
    print(seed)
    update_index()
