// Reduced excerpt of from_metadata23 / from_project_maybe_workspace on failing_ref
// crates/uv-distribution/src/metadata/requires_dist.rs
// 77f271063993020770ee785469226e33324576be
// No uv workspace (Poetry layout) -> Requirement::from with no git_member.

    pub fn from_metadata23(metadata: uv_pypi_types::RequiresDist) -> Self {
        Self {
            name: metadata.name,
            requires_dist: Box::into_iter(metadata.requires_dist)
                .map(Requirement::from)
                .collect(),
            provides_extra: metadata.provides_extra,
            dependency_groups: BTreeMap::default(),
            dynamic: metadata.dynamic,
        }
    }

        let Some(project_workspace) =
            ProjectWorkspace::from_maybe_project_root(install_path, &discovery, cache).await?
        else {
            return Ok(Self::from_metadata23(metadata));
        };
