
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name" protobuf:"bytes,1,opt,name=name"`
}
