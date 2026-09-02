// Reduced excerpt of ModuleLoader::load on failing_ref
// compiler-core/src/build/module_loader.rs
// leftover cache HIT when restored source fingerprint matches.

if meta.mtime < source_mtime {
    let source_module = read_source(name.clone())?;
    if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
        return Ok(Input::New(source_module));
    } else if self.mode == Mode::Lsp && self.incomplete_modules.contains(&name) {
        return Ok(Input::New(source_module));
    }
}
Ok(Input::Cached(self.cached(name, meta)))
