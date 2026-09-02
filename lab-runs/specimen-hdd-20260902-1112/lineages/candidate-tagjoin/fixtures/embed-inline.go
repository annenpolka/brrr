package v1

type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}

type HostAlias struct {
	Base `json:",inline"`
}

type Base struct {
	IP string `json:"ip,omitempty"`
}
