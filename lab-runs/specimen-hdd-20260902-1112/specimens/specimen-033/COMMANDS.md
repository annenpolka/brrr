# COMMANDS

Not executed in this packet. Commands as reported.

```bash
mkdir repro && cd repro && npm init -y
npm install vite --cache ./.cache
grep -rl playwright .cache/_cacache/index-v5
ls node_modules | wc -l
```

Arborist unit tests live in `workspaces/arborist/test/arborist/build-ideal-tree.js`. The production path is `workspaces/arborist/lib/arborist/build-ideal-tree.js` (`#loadPeerSet`).

```bash
git clone https://github.com/npm/cli.git
cd cli
git checkout 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862
```
