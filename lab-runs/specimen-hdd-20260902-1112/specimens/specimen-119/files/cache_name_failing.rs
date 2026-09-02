// Reduced excerpt of ExecutableTask::cache_name on failing_ref
// src/task/executable_task.rs
// 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
// Cache lives under the workspace task-cache folder.
// Filename is run-environment + task-name only.

    /// We store the hashes of the inputs and the outputs of the task in a file
    /// in the cache. The current name is something like
    /// `run_environment-task_name.json`.
    pub(crate) fn cache_name(&self) -> String {
        format!(
            "{}-{}.json",
            self.run_environment.name(),
            self.name().unwrap_or("default")
        )
    }
