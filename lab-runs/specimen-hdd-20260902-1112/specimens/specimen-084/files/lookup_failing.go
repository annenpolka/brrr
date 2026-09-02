# Reduced excerpt of Client.Lookup on failing_ref
# sumdb/client.go
# After ParseRecord / mergeLatest / checkRecord, the cache payload is `data`
# (full HTTP body). Identity extraction scans that payload for prefix
# path + " " + vers + " ".

		id, text, treeMsg, err := tlog.ParseRecord(data)
		if err != nil {
			return cached{nil, err}
		}
		if err := c.mergeLatest(treeMsg); err != nil {
			return cached{nil, err}
		}
		if err := c.checkRecord(id, text); err != nil {
			return cached{nil, err}
		}

		if writeCache {
			c.ops.WriteCache(file, data)
		}

		return cached{data, nil}
	}).(cached)
	if result.err != nil {
		return nil, result.err
	}

	prefix := path + " " + vers + " "
	var hashes []string
	for line := range strings.SplitSeq(string(result.data), "\n") {
		if strings.HasPrefix(line, prefix) {
			hashes = append(hashes, line)
		}
	}
	return hashes, nil
