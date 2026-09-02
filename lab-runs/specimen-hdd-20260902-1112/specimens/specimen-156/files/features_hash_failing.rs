// Reduced excerpt of Features::hash_for_runtime_transpiler on failing_ref
// src/js_parser/parser.rs
// b5d0bbc0edd90c46b29eb8273bc272a7042e584b
// define table / --drop omitted from the cache key.

fn hash_for_runtime_transpiler(&self, hasher: &mut Wyhash) {
    let bools: [bool; 17] = [ /* top_level_await .. repl_mode */ ];
    hasher.update(bytemuck::cast_slice::<bool, u8>(&bools));
    hasher.update(&[self.react_compiler as u8]);
    // --feature flags hashed
    // define / --drop NOT hashed
}
