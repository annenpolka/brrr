KNOWN FIX (sealed): rust-lang/cargo PR 16744 merge cbb9bb8bd0fb272b1be0d63a010701ecb3d1d6d3.

failing_ref is merge first parent 843a683fef61e9b3f9607ab637b72b0774241513.

Repair stores GitRemote.url as String. SCP-like child URLs convert to ssh:// only for SourceId; original string is kept for fetch and messages via GitSource::new_for_submodule. absolute_submodule_url no longer flips alternative form off. Test dep_with_scp_like_submodule_url expects git@github.com:foo/bar.git in stderr. SourceId still cannot be SCP-like.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
