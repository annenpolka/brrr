# TASK

Compose-go `Normalize` can keep the identity of a **previous image ENV default** after the compose file listed `FOO` (no equals, no value) and that listing should have meant unset-in-container. `resolve` drops a listed-without-equals name when the user environment has no matching entry. The service environment map then omits `FOO`. The leftover identity is the image `ENV FOO=not_empty` default, not unset.

On failing_ref `65600cee45d45771a1faa6ddaf87b23ca4d2400c`:

```
func resolve(a any, fn func(s string) (string, bool)) (any, bool) {
    switch v := a.(type) {
    case []any:
        var resolved []any
        for _, val := range v {
            if r, ok := resolve(val, fn); ok {
                resolved = append(resolved, r)
            }
        }
        return resolved, true
    case map[string]any:
        resolved := map[string]any{}
        for key, val := range v {
            if val != nil {
                resolved[key] = val
                continue
            }
            if s, ok := fn(key); ok {
                resolved[key] = s
            }
        }
        return resolved, true
    case string:
        if !strings.Contains(v, "=") {
            if val, ok := fn(v); ok {
                return fmt.Sprintf("%s=%s", v, val), true
            }
            return "", false
        }
        return v, true
    default:
        return v, false
    }
}
```

`service["environment"]` and `build["args"]` both call the same `resolve`. Listed-without-equals `FOO` with no user-env match returns `("", false)` and is dropped. `FOO=` (equals, empty) is a different identity and is kept. Image `ENV EMPTY=not_empty` then supplies leftover `not_empty`.

Public report (docker/compose#11962). Image `ENV EMPTY=not_empty`; compose lists `- EMPTY`; `echo "=$EMPTY="` prints `=not_empty=` (leftover image default) instead of `==` (unset). `FOO=` empty string is `==` with empty. User-env `EMPTY=hello` is `=hello=`.

In-tree after the repair (not on failing_ref): `resolve(a, fn, keepEmpty bool)`; environment uses `keepEmpty=true` and keeps listed-without-equals as `nil` / the bare name. Build args stay `keepEmpty=false`.

Case A — listed `FOO`, user env has `FOO=bar`:
  current resolved identity `FOO=bar`
  not leftover-after-drop

Case B — listed `FOO` (no equals), user env has no `FOO`, leftover drop:
  leftover: previous image ENV default / omitted from service environment
  listed-without-equals dropped (`"", false`)
  container still has image default

Case C — listed `FOO=` (equals, empty string):
  empty-string identity
  not unset; not leftover image default

Case D — environment keepEmpty (post-repair shape, not on failing_ref):
  listed-without-equals kept as nil / bare name
  container unsets; not leftover image default

The developer wants to know which identity case B actually used for `FOO` after the listing: leftover previous-image default (listed-without-equals dropped), current unset, empty string, or omitted (no env map).
