// Reduced excerpt of ExecutableTask::cache_name on failing_ref
// src/task/executable_task.rs
// 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
// Filename identity is run-environment + task-name.
// ArgValues / rendered inputs/outputs are omitted from the filename.

    pub(crate) fn cache_name(&self) -> String {
        format!(
            "{}-{}.json",
            self.run_environment.name(),
            self.name().unwrap_or("default")
        )
    }

    pub(crate) async fn can_skip(&self, lock_file: &LockFile) -> Result<CanSkip, std::io::Error> {
        let cache_name = self.cache_name();
        let cache_file = self.project().task_cache_folder().join(cache_name);
        // ...
    }
