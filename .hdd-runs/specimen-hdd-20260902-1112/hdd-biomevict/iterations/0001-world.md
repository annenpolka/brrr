# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public biomejs/biome#11409 (merged 2026-08-19). Squash `405dedb0ff65dd29927faf587f6542e3c29db248` (parent `7dbf9d84125b51c4177a899f8638d54b01cd065c`). Local biome was not performed on this lab host.

PR title: fix(core): files eviction and project. Closing a file would not evict the parsed-source map from the database. Changeset: LSP memory leak over long editor sessions.

On failing_ref, `close_file` removes `documents` and `node_cache` only. Parsed-source map stays. Project close unloads documents under the root but omitted descendant files-map eviction.

Not this packet: specimen-157 jest haste mock-name delete. specimen-159 gleam leftover cache files after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 7dbf9d84125b51c4177a899f8638d54b01cd065c
# crates/biome_service/src/workspace/server.rs close_file
# crates/biome_service/src/db/mod.rs WorkspaceDbData

# public shape:
# leftover parsed source after close_file
# documents/node_cache removed; files map omitted from eviction
# never-opened / db_remove_file drops the path
```

Source-backed only. Do not execute untrusted checkouts on the host.

biomejs/biome
  crates/biome_service/src/workspace/server.rs
  crates/biome_service/src/db/mod.rs
  crates/biome_service/src/db/state.rs
  crates/biome_service/src/workspace/server.tests.rs

RELEVANT MATERIAL

### close_file_failing.rs

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

### leftover_identity_split.txt

Registry / fixture:
  Biome workspace close_file / WorkspaceDb parsed-source map
  leftover ParsedSource after close

Case A (file still open, content unchanged):
  current parse identity
  not leftover-after-close

Case B (file closed, leftover parsed source):
  leftover: previous ParsedSource for that path
  documents/node_cache gone; files map omitted from eviction

Case C (never opened / empty workspace db):
  no parse
  not leftover previous source

Case D (db_remove_file on close):
  path gone from files map
  not leftover previous parse

Not this packet:
  jest haste mock-name delete (specimen-157)
  gleam leftover cache after move+restore (specimen-159)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
