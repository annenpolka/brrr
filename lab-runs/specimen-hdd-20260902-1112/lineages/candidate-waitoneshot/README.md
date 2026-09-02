# waitoneshot

For wait flags, say whether timeout 0 still visits the object or aborts on
a creation-wait default.

Timeout 0 is documented as check once. With wait-for-creation default true,
that path errors before looking at the object. The error looks like a user
mistake. It does not name abort-before-visit versus a one-shot check.

Disabling wait-for-creation, or using for=delete (the flag is ignored there),
restores the one-shot visit. This command prints that join from flag records.
There is no cluster.

## Usage

```
waitoneshot --timeout SECONDS [--wait-for-creation true|false] [--for COND] [--object-exists true|false]
python3 waitoneshot.py --timeout SECONDS ...
```

| flag | meaning |
| --- | --- |
| `--timeout` | wait budget. `0` is the documented one-shot value |
| `--wait-for-creation` | creation-wait default. `true` (default) or `false` |
| `--for` | condition name. `delete` ignores wait-for-creation. Default `jsonpath` |
| `--object-exists` | whether the object is already present. Default `true` |

`waitoneshot` is a launcher over `waitoneshot.py`. `decide()` is the table.

## Output

Two spaces between field and value.

```
timeout  0.0
wait_for_creation  true
for  jsonpath
object_exists  true
visited  false
oneshot  false
abort  wait-for-creation-requires-timeout
reason  creation-wait default aborts before lookup when timeout is 0
```

| field | meaning |
| --- | --- |
| `visited` | whether the object is looked at |
| `oneshot` | whether this is the documented timeout-0 check-once path |
| `abort` | `wait-for-creation-requires-timeout` or `none` |
| `reason` | abort-before-lookup, one-shot check, wait path, or would-wait |

## Examples

Abort before visit (timeout 0, wait-for-creation default true):

```
waitoneshot --timeout 0 --wait-for-creation true --for jsonpath --object-exists true
# visited  false
# oneshot  false
# abort  wait-for-creation-requires-timeout
```

One-shot visit (timeout 0, wait-for-creation false):

```
waitoneshot --timeout 0 --wait-for-creation false --for jsonpath --object-exists true
# visited  true
# oneshot  true
# abort  none
```

One-shot visit (`--for=delete`, flag ignored):

```
waitoneshot --timeout 0 --wait-for-creation true --for delete --object-exists true
# visited  true
# oneshot  true
# abort  none
```

## Boundary

Does not talk to a kube API, start a cluster, or evaluate jsonpath on a live
object. Missing-object plus a positive timeout is labeled wait-path, not
oneshot, and is not executed. `for=delete` is the harvest/help-text rule
(flag ignored), not a cluster transcript.
