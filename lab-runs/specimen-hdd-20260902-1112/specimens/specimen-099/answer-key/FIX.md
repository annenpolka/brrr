KNOWN FIX (sealed): rust-lang/cargo PR 16246 squash merge 0101bde5602af3625c2014fec9b0c497b3e7ef1f.

failing_ref is merge first parent e91b2baa632c0c7e84216c91ecfe107c37d887c1.

Submodule update fetched+reset into the checkout working copy. Parent git deps already used GitDatabase under git/db. Nested submodules did not, so a shared submodule URL was re-fetched and could not be reconstructed offline after deleting checkouts.

Repair: GitSource::fetch_db extracted from GitSource::update. update_submodule builds SourceId::for_git(url, Rev(head)).with_git_precise(head) and fetch_db(true)+copy_to. copy_to already recurses; extra recursive update after reset removed. Tests assert git/db/<submodule-ident> created once; dep_with_cached_submodule covers two parents one submodule.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
