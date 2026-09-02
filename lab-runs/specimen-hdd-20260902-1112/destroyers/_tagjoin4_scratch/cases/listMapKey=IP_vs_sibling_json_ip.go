
type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	Addr string `json:"address"`
	IP string `json:"ip,omitempty"`
}
