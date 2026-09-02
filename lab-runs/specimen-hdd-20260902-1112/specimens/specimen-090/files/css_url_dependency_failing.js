// Reduced excerpt of CssUrlDependency on failing_ref
// lib/dependencies/CssUrlDependency.js
// 66a8bcccc501ee1985a3b77d275ccc98df523346
// No updateHash. Template substitutes data.url["css-url"] at code-gen time.

class CssUrlDependency extends ModuleDependency {
  constructor(request, range, urlType) {
    super(request);
    this.range = range;
    this.urlType = urlType;
  }

  get type() {
    return "css url()";
  }

  createIgnoredModule(context) {
    return getIgnoredRawDataUrlModule();
  }

  serialize(context) {
    const { write } = context;
    write(this.urlType);
    super.serialize(context);
  }
}

CssUrlDependency.Template = class CssUrlDependencyTemplate extends (
  ModuleDependency.Template
) {
  apply(dependency, source, { type, moduleGraph, codeGenerationResults }) {
    if (type === "javascript") return;
    const dep = dependency;
    const module = moduleGraph.getModule(dep);
    let newValue;
    switch (dep.urlType) {
      case "url":
        newValue = `url(${cssEscapeString(
          this.assetUrl({ module, codeGenerationResults })
        )})`;
        break;
    }
    source.replace(dep.range[0], dep.range[1] - 1, newValue);
  }

  assetUrl({ runtime, module, codeGenerationResults }) {
    if (!module) return "data:,";
    const codeGen = codeGenerationResults.get(module, runtime);
    const data = codeGen.data;
    if (!data) return "data:,";
    const url = data.get("url");
    if (!url || !url["css-url"]) return "data:,";
    return url["css-url"];
  }
};
