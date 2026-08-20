package repo

import "fmt"

func hunk(line string) error {
	return fmt.Errorf("malformed hunk header missing old range: %s", line)
}
