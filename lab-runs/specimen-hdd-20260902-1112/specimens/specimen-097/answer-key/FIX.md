KNOWN FIX (sealed): moby/buildkit PR 5444 merge 94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9.

failing_ref is merge first parent bc6f7be35057d15f8384c91ed500a610ab7e2a87.

shaToCacheKey took only sha (+ ".git" if KeepGitDir, + ":" + subdir). CacheKey never passed the ls-remote usedRef. Two named refs at one commit therefore shared one keep-git-dir snapshot whose .git was fetched for the first ref.

Repair: shaToCacheKey(sha, ref) appends "#" + ref when KeepGitDir and ref != "". CacheKey records usedRef from ls-remote (partial/HEAD/tag). Commit-SHA identifiers still pass ref "". Added TestMultipleTagAccess / TestMultipleTagAccessKeepGitDir (two tags a/v1.2.3 and a/v1.2.3-same; keepGitDir requires key1 != key2, pin equal). keepGitDir false still keys equal. Existing keep-git-dir clones can miss after the key change.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
