# COMMANDS

```
# chart/values.yaml: data: {}
# values.yaml:
#   data:
#     foo: bar
#     baz: ~

helm template chart --values values.yaml
# helm v4.0.2: data: "map[foo:bar]"
# helm v3.19.3: data: "map[baz:<nil> foo:bar]"

# chart/values.yaml edited to: data: ~
helm template chart --values values.yaml
# helm v4.0.2: data: "map[baz:<nil> foo:bar]"
```

Not executed on this lab host.
