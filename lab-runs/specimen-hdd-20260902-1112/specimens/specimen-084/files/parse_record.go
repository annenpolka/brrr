# Reduced excerpt of record / tree encoding on failing_ref
# sumdb/tlog/note.go
# ParseRecord stops at the first blank line. Remainder is the signed tree note.
# ParseTree ignores extra lines after the three-line tree encoding.

func FormatTree(tree Tree) []byte {
	return fmt.Appendf(nil, "go.sum database tree\n%d\n%s\n", tree.N, tree.Hash)
}

// A future backwards-compatible encoding may add additional lines,
// which the parser can ignore.

func ParseRecord(msg []byte) (id int64, text, rest []byte, err error) {
	i := bytes.IndexByte(msg, '\n')
	id, err = strconv.ParseInt(string(msg[:i]), 10, 64)
	msg = msg[i+1:]
	i = bytes.Index(msg, []byte("\n\n"))
	text, rest = msg[:i+1], msg[i+2:]
	return id, text, rest, nil
}
