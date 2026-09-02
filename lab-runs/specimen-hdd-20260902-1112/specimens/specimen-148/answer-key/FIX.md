KNOWN FIX (sealed): containers/buildah PR 4526 merge 3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9.

failing_ref is first parent 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4.

RUN --mount=from=stage reused leftover previous layer after the source stage was rebuilt. StageMountDetails stored MountPoint only; whether that stage executed this build was omitted from cache identity.

PR repair: DidExecute on StageMountDetails; if any mounted stage DidExecute, avoidLookingCache.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
