# TASK

Biome's workspace database can keep the identity of a **previous parsed source** after `close_file`, because close removed the document and node_cache and omitted eviction of the parsed-source map (`db_remove_file`). The path-keyed parse stays. Memory grows across a long LSP session. A later open of the same path can see leftover previous parse.

On failing_ref `7dbf9d84125b51c4177a899f8638d54b01cd065c`:

```
fn close_file(&self, params: CloseFileParams) -> Result<(), WorkspaceError> {
    let path = params.path.as_path();

    self.documents.pin().remove(path);
    self.node_cache.lock().unwrap().remove(path);

    if self.is_indexed(path) {
        self.scanner.reindex_file(path.to_path_buf());
    }

    Ok(())
}
```

`WorkspaceDbData` clones used by Salsa queries did not carry a `files` map that close could pin-remove. `close_file` never called `db_remove_file`. Closing a project similarly omitted descendant parsed-source eviction from that map.

Public report (biomejs/biome#11409). Open files, close them, memory keeps growing; parsed sources stay. Expected: path gone from the parsed-source map. Actual: leftover previous parse.

In-tree after the repair (not on failing_ref): `WorkspaceDbData` holds `files`; `close_file` calls `db_remove_file`; `unload_path` drops descendant files.

Case A — file still open, content unchanged:
  parse identity is current
  not leftover-after-close

Case B — file closed, leftover parsed source:
  leftover: previous ParsedSource for that path
  documents/node_cache gone; files map omitted from eviction
  path-keyed HIT

Case C — never opened / empty workspace db:
  no parse
  not leftover previous source

Case D — db_remove_file on close (post-repair shape, not on failing_ref):
  path gone from files map
  not leftover previous parse

The developer wants to know which identity case B actually used for the path after close: leftover previous-parse (files map omitted from eviction), current disk, or omitted (no parse).
