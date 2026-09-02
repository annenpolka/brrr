// Reduced excerpt of compiledTask / Name on failing_ref
// variables.go / taskfile/ast/task.go
// 1e2121a99f6414e3bf4565e5736a116bef10be91
// Task name is the template. MATCH is not the checksum key.

	new := ast.Task{
		Task: origTask.Task,
		// no FullName
	}

func (t *Task) Name() string {
	if t.Label != "" {
		return t.Label
	}
	return t.Task
}
