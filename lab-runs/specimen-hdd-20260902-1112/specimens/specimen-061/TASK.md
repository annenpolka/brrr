# TASK
Two scripts. A: `true && echo ok` step status 0, all commands 0. B: `false || echo ok` step status 0, first command 1. Only observed difference is whether a nonzero was swallowed.
