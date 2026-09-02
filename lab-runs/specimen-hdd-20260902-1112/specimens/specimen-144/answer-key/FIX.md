KNOWN FIX (sealed): GoogleContainerTools/skaffold PR 9278 squash 9ff4546df8c0d891fde32c24e0d0ef93a8c7404b.

failing_ref is parent 6ea9aeb818b8e371a4386bf044479f86a0a6e885.

lookupRemote returned found whenever RemoteDigest(tag) succeeded, so leftover previous image identity after the same tag was reused with a different input digest.

PR repair: return found only when cacheHit and remoteDigest == cachedEntry.Digest.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
