// Reduced excerpt of resolve on failing_ref
// loader/normalize.go
// 65600cee45d45771a1faa6ddaf87b23ca4d2400c
// listed-without-equals with no user-env match returns "", false and is dropped.
// leftover identity is the image ENV default.

func resolve(a any, fn func(s string) (string, bool)) (any, bool) {
    switch v := a.(type) {
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

// service["environment"] and build["args"] share this resolve
