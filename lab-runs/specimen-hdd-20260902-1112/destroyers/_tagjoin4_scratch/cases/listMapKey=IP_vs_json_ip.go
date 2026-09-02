
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"IP,omitempty"`
}
