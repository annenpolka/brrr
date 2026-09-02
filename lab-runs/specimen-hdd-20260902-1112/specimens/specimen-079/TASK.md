# TASK

`helm template` of a chart whose default `values.yaml` is an empty map, plus a user values file that sets a key in that map to YAML null, drops the null key from `.Values`.

Chart `values.yaml`:

```
data: {}
```

User `values.yaml`:

```
data:
  foo: bar
  baz: ~
```

Template `templates/foo.yaml`:

```
data: {{.Values.data | quote}}
```

Helm v4.0.2 (`GitCommit: 94659f25033af6eb43fc186c24e6c07b1091800b`):

```
$ helm template chart --values values.yaml
---
# Source: foo/templates/foo.yaml
data: "map[foo:bar]"
```

Same files on helm v3.19.3 (`GitCommit: 0707f566a3f4ced24009ef14d67fe0ce69db4be9`):

```
data: "map[baz:<nil> foo:bar]"
```

If only the chart default is changed from `data: {}` to `data: ~`, helm v4.0.2 keeps `baz`:

```
data: "map[baz:<nil> foo:bar]"
```

The developer wants to know which identity of `baz` `.Values.data` actually contained after coalesce for each chart default (`{}` vs `~`): omitted key versus present-nil.
