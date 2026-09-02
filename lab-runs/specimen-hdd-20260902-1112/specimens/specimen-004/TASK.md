# TASK

`npm install vite` into an empty project installs about 10 packages but, with a cold cache, also downloads full registry metadata for many packages that do not end up installed (playwright, @types/node, webdriverio, jsdom, sass, less, terser, vitest's optional peers, ...).

The developer wants to know *why those fetches happened* and which dependency edges caused work that the final tree does not use.
