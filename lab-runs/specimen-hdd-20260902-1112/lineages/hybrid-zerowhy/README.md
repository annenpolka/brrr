# zerowhy

Classify a lying zero / green as **exactly one** of:

`swallowed-nonzero` | `abort-before-visit` | `observed-ok` | `unknown`

Parents each name one way a zero can lie. `swallowecho` reports that `||`
hid a nonzero while the step stayed 0. `waitoneshot` reports that timeout 0
aborted before visiting the object. Concatenating those reports still
leaves a hand join: which one *is* this green? This query is that exclusive
class.

## Usage

```
zerowhy 'false || echo ok'
zerowhy --timeout 0 --wait-for-creation true
zerowhy --timeout 0 --wait-for-creation false --object-exists true
zerowhy --timeout 0 --wait-for-creation true -- 'false' '||' echo ok
```

| input | meaning |
| --- | --- |
| snippet | small shell list: `true` / `false` / `echo` / `printf` / `:`, with `\|\|`, `&&`, `\|`, `;` |
| `-- WORD ...` | argv list; `\|\|` / `&&` are tokens |
| `--timeout` | wait budget. Presence turns on wait evidence. `0` is oneshot |
| `--wait-for-creation` | `true` (default with `--timeout`) or `false` |
| `--for` | condition name. `delete` ignores wait-for-creation. Default `jsonpath` |
| `--object-exists` | whether the object is already present. Default `true` |

Need a snippet and/or `--timeout`. One invocation. Not two parent CLIs.

## Output

Two spaces between field and value.

```
why  swallowed-nonzero
claims  swallowed-nonzero
detail  || hid a nonzero; step status 0
```

| field | meaning |
| --- | --- |
| `why` | the exclusive class |
| `claims` | parent-derived reasons before the XOR. `none` if neither parent names this zero |
| `detail` | one-line join, not parent stdout |

If both parents claim a reason (`||` swallow **and** abort-before-visit),
`why` is `unknown` and `claims` lists both. That refusal is the join.

## Examples

```
zerowhy 'false || echo ok'
# why  swallowed-nonzero

zerowhy --timeout 0 --wait-for-creation true
# why  abort-before-visit

zerowhy --timeout 0 --wait-for-creation false --object-exists true
# why  observed-ok
```

`true && echo ok` is `observed-ok`. `false; echo ok` is `unknown` (`;`
last-status is not this `||` swallow). Timeout 0 without creation-wait on a
missing object is `unknown` (no visit, no abort).

## Boundary

Does not run Bazel, kubectl, or a cluster. Unmodeled heads (`make`, `bazel`)
are a refusal, not a guessed status. Does not concatenate `swallowecho` and
`waitoneshot` stdout.
