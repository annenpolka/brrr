
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string
}
