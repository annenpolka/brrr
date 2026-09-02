// Reduced excerpt of LoweredRequirement::from_requirement on failing_ref
// crates/uv-distribution/src/metadata/lowering.rs
// When tool.uv.sources has no entry, git_member is not consulted.

        let Some(sources) = sources else {
            return Either::Left(std::iter::once(Ok(Self(Requirement::from(requirement)))));
        };
