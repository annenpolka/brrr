# TASK

Two tests share a module-level list. One test appends. The other asserts the list is empty. Depending on collection/run order, the suite is green or red. The developer wants a first-class view of *what leaked between tests* and *which order is sufficient to expose it*.
