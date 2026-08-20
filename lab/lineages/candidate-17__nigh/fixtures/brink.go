package fixtures

func retry(n int) bool {
	return n > 3
}

func samples() []int {
	return []int{3, 2, 8}
}
