// Reduced excerpt of AssetGenerator.generate on failing_ref
// lib/asset/AssetGenerator.js
// 66a8bcccc501ee1985a3b77d275ccc98df523346
// Leftover persisted data.url[type] is spread AFTER the new value, so it wins.
// type for CSS substitution is "css-url" (CSS_URL_TYPE).

      if (data) {
        data.set("url", { [type]: content, ...data.get("url") });
      }

      // resource (non-dataUrl) branch, later in generate:

      if (data && (type === JAVASCRIPT_TYPE || type === CSS_URL_TYPE)) {
        data.set("url", { [type]: assetPath, ...data.get("url") });
      }
