# adrid

Name when a done-set address no longer names the same lock node.

```
addrid RECORD
```

| field | meaning |
| --- | --- |
| `insert ADDR NAME` | address entered done as NAME |
| `worker ADDR NAME` | later work saw ADDR as NAME |
| `fetched NAME` | input actually fetched |

`reused` is same address, different name. `skipped` is inserted/worker names never fetched.
