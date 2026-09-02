// Reduced excerpt of Node.addEdgeIn on failing_ref
// workspaces/arborist/lib/node.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// Incoming override set overwrites this.overrides. Out-edges are not walked.

  addEdgeIn (edge) {
    if (edge.overrides) {
      this.overrides = edge.overrides
    }

    this.edgesIn.add(edge)

    // try to get metadata from the yarn.lock file
    if (this.root.meta) {
      this.root.meta.addEdge(edge)
    }
  }
