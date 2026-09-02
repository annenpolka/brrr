KNOWN FIX (sealed): gruntwork-io/terragrunt PR 774 merge 85f63b2bbde2fc8d9b207799e6891c171e6527ee.

failing_ref is first parent 17004093f058bfe45c59ab6e34fe3c46da86dbf8.

.encodeSourceName omitted ref from cache-path identity so leftover dest was reused. CopyFolderContents had no manifest, so leftover previous files (stale.tf) stayed after source change. cleanupDownloadDir wiped .git in that leftover dest.

PR repair: fileManifest Clean() of previously copied paths; CopyFolderContents takes manifestFile; cleanupDownloadDir removed.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
