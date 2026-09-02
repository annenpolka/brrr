package v1

type Bag struct {
	// +listType=map
	// +listMapKey=name
	Items []Item `json:"items,omitempty"`
}

type Item struct {
	Name string `json:"name"`
	Value string `json:"value,omitempty"`
}
