# Reduced excerpt of checkRecord on failing_ref
# sumdb/client.go
# Authenticates ParseRecord's `text` against tiles. Does not hash the
# signed tree note or its extra lines.

func (c *Client) checkRecord(id int64, data []byte) error {
	c.latestMu.Lock()
	latest := c.latest
	c.latestMu.Unlock()

	if id >= latest.N {
		return fmt.Errorf("cannot validate record %d in tree of size %d", id, latest.N)
	}
	hashes, err := tlog.TileHashReader(latest, &c.tileReader).ReadHashes([]int64{tlog.StoredHashIndex(0, id)})
	if err != nil {
		return err
	}
	if hashes[0] == tlog.RecordHash(data) {
		return nil
	}
	return fmt.Errorf("cannot authenticate record data in server response")
}
