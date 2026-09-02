// Reduced excerpt of Edge.reload / detach on failing_ref
// workspaces/arborist/lib/edge.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// Target OverrideSet is not recomputed when the incoming edge is dropped.

  reload (hard = false) {
    this.#explanation = null
    if (this.#from.overrides) {
      this.overrides = this.#from.overrides.getEdgeRule(this)
    } else {
      delete this.overrides
    }
    const newTo = this.#from.resolve(this.#name)
    if (newTo !== this.#to) {
      if (this.#to) {
        this.#to.edgesIn.delete(this)
      }
      this.#to = newTo
      this.#error = null
      if (this.#to) {
        this.#to.addEdgeIn(this)
      }
    } else if (hard) {
      this.#error = null
    }
  }

  detach () {
    this.#explanation = null
    if (this.#to) {
      this.#to.edgesIn.delete(this)
    }
    this.#from.edgesOut.delete(this.#name)
    this.#to = null
    this.#error = 'DETACHED'
    this.#from = null
  }
