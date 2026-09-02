# Reduced excerpt of enqueue_dependency_with_main_and_success_fn on failing_ref
# src/install/PackageManager/PackageManagerEnqueue.rs
# Fresh resolve does not populate an optional-peer slot independently.

pub fn enqueue_dependency_with_main_and_success_fn(
    this: &mut PackageManager,
    id: DependencyID,
    dependency: &Dependency,
    resolution: PackageID,
    install_peer: bool,
    success_fn: SuccessFn,
    fail_fn: Option<FailFn>,
    is_root: bool,
) -> crate::Result<()> {
    if dependency.behavior.is_optional_peer() {
        return Ok(());
    }
    // ... remaining enqueue omitted ...
}
