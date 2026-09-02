# TASK

stylelint `--cache` can keep the identity of a **previous lint result** after a config-file change should have been a different cache object. `standalone` hashed `JSON.stringify(config || {})` before cosmiconfig resolution. When the CLI config object is undefined (config loaded from `.stylelintrc.json`), that hash is stylelintVersion plus "{}". Resolved file config is omitted.

On failing_ref `3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66`:

```
const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);
fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);
absoluteFilePaths = absoluteFilePaths.filter(fileCache.hasFileChanged.bind(fileCache));
```

Public report (stylelint/stylelint#2908). `.stylelintrc.json` with `block-no-empty: null` then change to `true`; leftover `.stylelintcache` still skips `a.css`.

In-tree after the repair (not on failing_ref): `lintSource` calls `calcHashOfConfig(config)` after `getConfigForFile`; test `cache is discarded when a config file is changed`.

Case A — second `stylelint --cache` with unchanged `.stylelintrc.json`:
  cache identity is current
  not leftover-after-config-change

Case B — config file rule flipped, leftover `.stylelintcache`:
  leftover: previous config's lint results
  resolved file config omitted from hash (`config || {}` is `{}`)
  new-rule warnings not reported

Case C — delete `.stylelintcache` then lint:
  fresh cache identity
  not leftover previous config

Case D — hash resolved config after getConfigForFile (post-repair shape, not on failing_ref):
  cache miss after config-file change
  not leftover previous results

The developer wants to know which identity case B actually used for `.stylelintcache` after the config-file change: leftover previous-config results (resolved config omitted), current config-file identity, or omitted (no cache file).
