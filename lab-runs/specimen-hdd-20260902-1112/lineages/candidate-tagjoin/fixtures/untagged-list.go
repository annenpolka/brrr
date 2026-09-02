package v1

type Spec struct {
	// +listMapKey=name
	Items []Item
}

type Item struct {
	Name string `json:"name,omitempty"`
}
