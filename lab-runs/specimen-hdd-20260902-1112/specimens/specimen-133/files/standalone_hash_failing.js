// Reduced excerpt of standalone cache identity on failing_ref
// lib/standalone.js
// 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
// CLI config (often undefined when using a file config) is hashed.
// Resolved cosmiconfig config is omitted.

		const stylelintVersion = pkg.version;
		const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);

		fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);
		absoluteFilePaths = absoluteFilePaths.filter(fileCache.hasFileChanged.bind(fileCache));
