// Reduced excerpt of PackageLoader::run on failing_ref
// compiler-core/src/build/package_loader.rs
// 3767575d05372e4b823c132afacb28e52fbe3aa1
// removed modules are marked stale; cache files stay.

for cache_file in gleam_cache_files(&self.io, &self.artefact_directory) {
    let module = module_name(&self.artefact_directory, &cache_file);
    if !inputs.contains_key(&module) {
        self.stale_modules.add(module);
    }
}
