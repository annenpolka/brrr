// Reduced excerpt of generateUniqueKeyPrefix on failing_ref
// internal/bundler/bundler.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff

func generateUniqueKeyPrefix() (string, error) {
    var data [12]byte
    rand.Seed(time.Now().UnixNano())
    if _, err := rand.Read(data[:]); err != nil {
        return "", err
    }
    // This is 16 bytes and shouldn't generate escape characters when put into strings
    return base64.URLEncoding.EncodeToString(data[:]), nil
}
