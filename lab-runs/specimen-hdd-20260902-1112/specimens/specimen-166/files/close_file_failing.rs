// Reduced excerpt of close_file on failing_ref
// crates/biome_service/src/workspace/server.rs
// 7dbf9d84125b51c4177a899f8638d54b01cd065c
// documents/node_cache removed; parsed-source map omitted from eviction.

fn close_file(&self, params: CloseFileParams) -> Result<(), WorkspaceError> {
    let path = params.path.as_path();

    self.documents.pin().remove(path);
    self.node_cache.lock().unwrap().remove(path);

    if self.is_indexed(path) {
        self.scanner.reindex_file(path.to_path_buf());
    }

    Ok(())
}
