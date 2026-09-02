# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

ESLint's `--cache` can keep the identity of a **previous lint result** after a plugin upgrade should have been a different cache object. Flat config serialization used as the cache identity listed plugins as namespaces only. Plugin `name@version` / `meta.name`+`meta.version` are omitted, so leftover cache after `eslint-plugin-react` 7.37.1 → 7.37.7 still hits.

On failing_ref `b3634f695ddab6a82c0a9b1d8695e62b60d23366`, `FlatConfigArray` `toJSON` does:

```
plugins: Object.keys(plugins),
```

Parser/processor objects already used `getObjectId` (name@version). Plugins did not.

Public report (eslint/eslint#16284): upgrade eslint-plugin-react; leftover cache suppresses new-rule offenses.

In-tree after the repair (not on failing_ref): serialize each plugin as `namespace:name@version` via `getObjectId`; tests convert config with plugin name/version and plugin meta into normalized JSON.

Case A — second `eslint --cache` with unchanged plugin version:
  cache identity is current
  not leftover-after-plugin-upgrade

Case B — plugin upgrade, leftover cache:
  leftover: previous plugin version's lint results
  plugin name@version omitted from serialized config identity
  new-rule offenses not reported

Case C — delete `.eslintcache` then lint:
  fresh cache identity
  not leftover previous plugin

Case D — plugin meta in serialized config (post-repair shape, not on failing_ref):
  cache miss after plugin upgrade
  not leftover previous plugin results

The developer wants to know which identity case B actually used for the ESLint cache after the plugin upgrade: leftover previous-plugin results (meta omitted), current plugin-version identity, or omitted (no cache file).

# OBSERVED

Public eslint/eslint#16284 (closed 2023-03-23). PR 16992 squash `1665c029acb92bf8812267f1647ad1a7054cbcb4` (parent `b3634f695ddab6a82c0a9b1d8695e62b60d23366`). Local ESLint was not performed on this lab host.

Issue body: leftover cache after eslint-plugin-react upgrade hid new-rule offenses. Related eslintrc#88 is not this packet (legacy eslintrc cache).

On failing_ref, `toJSON` serializes plugins as `Object.keys(plugins)` only. `getObjectId` for plugins is **not** on the failing revision. It is added by PR 16992.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-128 dart leftover package_config missing workspace member.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref b3634f695ddab6a82c0a9b1d8695e62b60d23366
# lib/config/flat-config-array.js FlatConfigArray toJSON plugins: Object.keys(plugins)

# public shape:
# leftover .eslintcache after eslint-plugin-react 7.37.1 -> 7.37.7
# plugin name@version omitted from serialized config identity
# new-rule offenses not reported
```

Source-backed only. Do not execute untrusted checkouts on the host.

eslint/eslint
  lib/config/flat-config-array.js
  tests/lib/config/flat-config-array.js
  docs/src/extend/plugins.md
  .eslintcache

RELEVANT MATERIAL

### flat_config_tojson_failing.js

// Reduced excerpt of FlatConfigArray toJSON on failing_ref
// lib/config/flat-config-array.js
// b3634f695ddab6a82c0a9b1d8695e62b60d23366
// Plugins serialized as namespaces only. Plugin name@version omitted.

                return {
                    ...this,
                    plugins: Object.keys(plugins),
                    languageOptions: {
                        ...languageOptions,
                        parser: parserName
                    },
                    processor: processorName
                };

### leftover_identity_split.txt

Registry / fixture:
  eslint --cache with eslint-plugin-react 7.37.1
  leftover .eslintcache after upgrade to 7.37.7

Case A (second lint, same plugin version):
  current cache identity
  not leftover-after-plugin-upgrade

Case B (plugin upgrade, leftover cache):
  leftover: previous plugin version results
  plugin name@version omitted from serialized config
  new-rule offenses not reported

Case C (delete .eslintcache):
  fresh cache identity
  not leftover previous plugin

Case D (plugin meta in serialized config):
  cache miss after upgrade
  not leftover previous plugin results

Not this packet:
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)
  dart leftover package_config missing workspace member (specimen-128)

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
