
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name,omitempty" protobuf:"bytes,1,opt,name=name"`
}
