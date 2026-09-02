# TASK

An npm/cli checkout sits at 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862 (npm 11.15.0 class of arborist).

From an empty project:

```
mkdir repro && cd repro && npm init -y
npm install vite --cache ./.cache
```

Ten packages end up in `node_modules`. The local cache still contains full packuments for packages that were never installed, including `playwright` (~16.6MB), `@types/node` (~11MB), `webdriverio`, `jsdom`, `sass`, `less`, `terser`, and further optional peers reached through `vite`'s optional peer on `vitest`.

pnpm and yarn, on the same package, do not fetch those packuments.

Outcome sought: why an unmet optional peer still causes a registry fetch, and how that fetch relates to the tree that is actually reified.
