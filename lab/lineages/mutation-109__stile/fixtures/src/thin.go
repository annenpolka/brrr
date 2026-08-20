package thin

func nl(cleaned string) string {
	return cleaned + "\n"
}

func ok(body string) string {
	return body + "\nOK"
}

func abcd(body string) string {
	return body + "abcd"
}

func colon(a, b string) string {
	return a + ":" + b
}

func openOnly(path string) string {
	return "open " + path
}

func fence(response func() string) string {
	return "```json\n" + response() + "\n```"
}

func unclosed(response func() string) string {
	return "```json\n" + response()
}
