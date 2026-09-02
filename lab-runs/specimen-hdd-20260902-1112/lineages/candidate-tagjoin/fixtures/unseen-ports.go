package v1

type Spec struct {
	// +listType=map
	// +listMapKey=containerPort
	Ports []ContainerPort `json:"ports,omitempty"`
}

type ContainerPort struct {
	ContainerPort int32 `json:"containerPort,omitempty"`
	Protocol string `json:"protocol"`
}
