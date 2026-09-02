// Reduced excerpt of RecomputeNodeDirty / LoadDepsFromLog on failing_ref
// src/graph.cc
// 77d328f5f679bfef14b1f67f3cd431b729bc786f
// Leftover deps-log identity is loaded before dirty is known.
// Validity is output mtime vs stored deps mtime. Dirty/command omitted.

  if (!edge->deps_loaded_) {
    edge->deps_loaded_ = true;
    if (!dep_loader_.LoadDeps(edge, err)) {
      dirty = edge->deps_missing_ = true;
    }
  }

bool ImplicitDepLoader::LoadDeps(Edge* edge, string* err) {
  string deps_type = edge->GetBinding("deps");
  if (!deps_type.empty())
    return LoadDepsFromLog(edge, err);
  // ...
}

bool ImplicitDepLoader::LoadDepsFromLog(Edge* edge, string* err) {
  Node* output = edge->outputs_[0];
  DepsLog::Deps* deps = deps_log_ ? deps_log_->GetDeps(output) : NULL;
  if (!deps) return false;
  if (output->mtime() > deps->mtime) return false;  // mtime only
  edge->inputs_.insert(..., nodes, nodes + node_count);
  return true;
}
