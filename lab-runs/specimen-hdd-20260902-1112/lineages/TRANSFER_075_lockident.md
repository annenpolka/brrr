# Transfer: specimen-075 / hdd-gocache onto lockident

Host-executed owned fixture `gocache_buildid.py`:

```
first BUILT key 55e3acdd667f buildid buildid-aaa
second FRESH key 55e3acdd667f buildid buildid-bbb cached_buildid buildid-aaa
same_key True
key_includes_buildid False
stale_binary True
```

lockident:

```
python3 lockident.py --identity 55e3acdd667f \
  --blob 'tests=["foo_test.go"]' --blob buildid=buildid-aaa --live tests
```

```
tests        55e3acdd667f in
buildid      5ad4c87a0014 omitted
in_identity  tests
omitted  buildid
live_lock_in_identity  true
```

The join is: FRESH identity is the test-file list; buildid is omitted; stale
binary is that miss. No new CLI.

Result: TRANSFER OK onto lockident.
