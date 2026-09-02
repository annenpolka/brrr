# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public stylelint/stylelint#2908 (closed 2022-09-27). PR 6356 squash `5be33b779b93761d86cb871dfd70f34686b5f6c5` (parent `3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66`). Local stylelint was not performed on this lab host.

Issue body: a config change is not detected when using `--cache`.

On failing_ref, standalone hashes the CLI `config` argument (often undefined when a file config is used) and filters paths before `lintSource`. `calcHashOfConfig` on the resolved config is **not** on the failing revision. It is added by PR 6356.

Not this packet: specimen-132 eslint leftover cache plugin name@version omitted from toJSON. specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
# lib/standalone.js hash(`${stylelintVersion}_${JSON.stringify(config || {})}`)

# public shape:
# leftover .stylelintcache after .stylelintrc.json block-no-empty null -> true
# resolved file config omitted from hash (CLI config undefined -> {})
# new-rule warnings not reported
```

Source-backed only. Do not execute untrusted checkouts on the host.

stylelint/stylelint
  lib/standalone.js
  lib/utils/FileCache.js
  lib/lintSource.js
  lib/__tests__/standalone-cache.test.js
  .stylelintcache
  .stylelintrc.json

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  .stylelintrc.json block-no-empty: null
  leftover .stylelintcache after flipping to true

Case A (second lint, same config file):
  current cache identity
  not leftover-after-config-change

Case B (config file flipped, leftover cache):
  leftover: previous config results
  resolved file config omitted (hash of {})
  new-rule warnings not reported

Case C (delete .stylelintcache):
  fresh cache identity
  not leftover previous config

Case D (hash resolved config after getConfigForFile):
  cache miss after file change
  not leftover previous results

Not this packet:
  eslint leftover plugin name@version omitted from toJSON (specimen-132)
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)

### standalone_hash_failing.js

// Reduced excerpt of standalone cache identity on failing_ref
// lib/standalone.js
// 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
// CLI config (often undefined when using a file config) is hashed.
// Resolved cosmiconfig config is omitted.

		const stylelintVersion = pkg.version;
		const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);

		fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);
		absoluteFilePaths = absoluteFilePaths.filter(fileCache.hasFileChanged.bind(fileCache));

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
