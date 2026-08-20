package ugly

import "fmt"

func openFile(path string, err error) error {
	return fmt.Errorf("open %s: %v", path, err)
}
