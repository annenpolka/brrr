package ugly

import (
	"errors"
	"fmt"
)

func openFile(path string, err error) error {
	// No sibling fmt.Errorf — invert/stump/lede extracted only "open ".
	return errors.New("open " + path + ": " + err.Error())
}

func openOnly(path string) string {
	return "open " + path
}

func sprintOpen(path string, err error) string {
	return fmt.Sprint("open ", path, ": ", err)
}

func failed(op, path, err string) string {
	return "failed " + op + " on " + path + " with " + err
}

// Expression-first: splice starts at a string and misses these.
func suffixErr(path string, err error) string {
	return path + ": " + err.Error()
}

func done(body string) string {
	return body + "\nDone."
}

func wrappedDone(body string) string {
	return body
		+ "\nDone."
}
