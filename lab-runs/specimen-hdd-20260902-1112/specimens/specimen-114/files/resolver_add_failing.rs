// Reduced excerpt of Resolver::add on failing_ref
// crates/ruff_workspace/src/resolver.rs
// 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
// Only {path}/{*filepath} is registered. Directory query misses.

        match self
            .router
            .insert(format!("{path}/{{*filepath}}"), self.settings.len() - 1)
        {
            Ok(()) => {}
            Err(InsertError::Conflict { .. }) => {}
            Err(_) => unreachable!("file paths are escaped before being inserted in the router"),
        }
