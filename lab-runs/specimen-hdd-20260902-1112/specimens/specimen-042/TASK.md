# TASK

A large multi-project Gradle build enables Isolated Projects and parallel configuration. Configuration sometimes fails on an arbitrary project with a `HashMap$Node` / `HashMap$TreeNode` ClassCastException inside `BuildScopeInMemoryCachingScriptClassCompiler.compile`.

The same build often succeeds on retry. The stack is in script-class compilation during project configuration, not in task execution.

The developer wants to know which cache is being mutated, which threads reach `compile()`, and why the failure names a project that did not change.
