package leftover

import "os"

func writeCleaned(path, cleaned string) error {
	return os.WriteFile(path, []byte(cleaned+"\n"), 0o644)
}

func stamp(ts, body string) string {
	return ts + " ERROR " + body
}

func spawn(cmd string) string {
	return "failed to spawn `" + cmd + "`"
}

func done(body string) string {
	return body + "\nDone."
}
