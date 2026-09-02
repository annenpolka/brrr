// Reduced excerpt of Node.overridden on failing_ref
// workspaces/arborist/lib/node.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// A leftover OverrideSet with name+value still reports overridden.

  get overridden () {
    return !!(this.overrides && this.overrides.value && this.overrides.name === this.name)
  }
