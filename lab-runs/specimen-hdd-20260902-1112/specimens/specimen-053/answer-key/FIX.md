KNOWN FIX (sealed): dependabot/dependabot-core PR 14944 merge ac2cd9a751975ecead87fa2a636ecdc212fc7276.

with_git_configured already uniquified the global gitconfig filename. The credential store stayed Dir.pwd/git.store, so turbo_tests workers clobbered each other's credentials.

Repair: one random_suffix for both #{suffix}.gitconfig and Dir.pwd/#{suffix}.git.store; pass git_store_path into configure_git_to_use_https_with_credentials; rm_f the store in ensure. Specs assert the unique .git.store name and cleanup.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
