// Reduced excerpt of expand_env + get_file_hashes on failing_ref
// crates/core/task/src/task.rs expand_env
// crates/core/vcs/src/git.rs get_file_hashes
// 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
// env file loaded into env vars. Not pushed onto inputs.
// Gitignored paths omitted from hash objects.

    pub fn expand_env(&mut self, data: &ResolverData) -> Result<(), TaskError> {
        if let Some(env_file) = &self.options.env_file {
            let env_path = data.project_root.join(env_file);
            // no self.inputs.push(env_file)
            for entry in dotenvy::from_path_iter(&env_path).map_err(error_handler)? {
                let (key, value) = entry.map_err(error_handler)?;
                self.env.entry(key).or_insert(value);
            }
        }
        Ok(())
    }

    async fn get_file_hashes(&self, files: &[String]) -> VcsResult<BTreeMap<String, String>> {
        let mut objects = vec![];
        for file in files {
            if !self.is_file_ignored(file) {
                objects.push(file.clone());
            }
        }
        // hash-object --stdin-paths on objects only
    }
