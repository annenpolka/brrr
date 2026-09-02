package v1

type Spec struct {
	// +listMapKey=Name
	Items []Item `json:"items"`
}

type Item struct {
	Name string `json:",omitempty"`
}
