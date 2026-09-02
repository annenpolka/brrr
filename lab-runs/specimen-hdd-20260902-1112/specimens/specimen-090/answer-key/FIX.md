KNOWN FIX (sealed): webpack/webpack PR 20938 squash merge c030e725c8c533f2838ff8424ae6444c23ef196a.

CssUrlDependency contributed nothing to the CSS module hash (Dependency.updateHash is empty; the class had no override), so [contenthash] with realContentHash false stayed H_css1 after a PNG-only byte change. Repair A: CssUrlDependency.updateHash now does hash.update(buildInfo.hash) of the moduleGraph module for this dependency, so the CSS module hash moves when the asset build hash moves. Repair B: AssetGenerator.generate previously did data.set("url", { [type]: assetPath, ...data.get("url") }), letting a persisted css-url win; the spread is flipped to { ...data.get("url"), [type]: assetPath } so the new path wins. Added watchCase long-term-caching/css-contenthash-asset-url step 2: CSS name !== STATE.cssName and emitted CSS contains the new PNG name.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
