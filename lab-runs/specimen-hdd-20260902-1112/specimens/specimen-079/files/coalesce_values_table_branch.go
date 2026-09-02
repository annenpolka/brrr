# Reduced excerpt of coalesceValues on failing_ref
# pkg/chart/common/util/coalesce.go
# dest/user values override chart vc.

for key, val := range vc {
	if value, ok := v[key]; ok {
		if value == nil && !merge {
			delete(v, key)
		} else if dest, ok := value.(map[string]interface{}); ok {
			src, ok := val.(map[string]interface{})
			if !ok {
				if val != nil {
					printf("warning: skipped value for %s.%s: Not a table.", subPrefix, key)
				}
			} else {
				merge := childChartMergeTrue(c, key, merge)
				coalesceTablesFullKey(printf, dest, src, concatPrefix(subPrefix, key), merge)
			}
		}
	} else {
		v[key] = val
	}
}
