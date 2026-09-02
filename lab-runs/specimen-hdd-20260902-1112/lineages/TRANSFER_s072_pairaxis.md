# Transfer: hdd-extraglobal / specimen-072 onto pairaxis

Host pairaxis on owned pairing traces:

```
n_diff  4
only_axis  multiple
diff  acc  left=[]  right=['a']
diff  flag  left=False  right=True
diff  order  ...
diff  test_b  PASS vs FAIL
```

Both leaked objects are named. leakorder cannot see nested tests (TRANSFER FAIL
on leakorder). pairaxis transfer holds; no new leak binary.

Result: TRANSFER OK onto pairaxis.
