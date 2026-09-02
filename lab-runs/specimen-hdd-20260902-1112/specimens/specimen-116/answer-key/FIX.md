KNOWN FIX (sealed): coder/coder PR 27987 squash df278ec0795cda3af53bae17aae5108ddcfe2d69.

failing_ref is squash parent 9a57dfa6424996d92daa18a8a5b96efcb1576a1a.

Unkeyed parse defaulted cacheKey to filename. Leftover highlight AST from the first diff of a path was reused for a later different body.

PR repair: stamp cacheKey from FNV-1a of that file's render inputs (name, prevName, lang, hunks, line arrays).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
