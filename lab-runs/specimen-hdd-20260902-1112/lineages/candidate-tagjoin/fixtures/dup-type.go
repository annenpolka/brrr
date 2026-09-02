package v1

type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}

type HostAlias struct {
	IP string `json:"ip"`
}

type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
