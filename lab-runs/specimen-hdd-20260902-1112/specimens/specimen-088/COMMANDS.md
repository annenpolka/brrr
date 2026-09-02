# COMMANDS

```
# failing_ref 040aac7031d900c2c548154fcbc75627b01e386c
# (not executed on this lab host)

# Case A — queried directory tree
# build.gradle: task report { def tree = fileTree("src"); def result = 'files=' + tree.files.name.sort(); doLast { println(result) } }
# src/file1, src/dir/file2
./gradlew report --configuration-cache
# run 1: Configuration cache entry stored. files=[file1, file2]
./gradlew report --configuration-cache
# run 2: Configuration cache entry reused. files=[file1, file2]
# then: create src/file3
./gradlew report --configuration-cache
# run 3: identity after the tree contents changed is the question

# Case B — fixed names, contents rewritten
# task report { def files = files("file1", "file2"); def result = files.files.name; doLast { println(result) } }
# after store+load: echo updated > file1
./gradlew report --configuration-cache
# documented: still load, still [file1, file2]

# Case C — fileTree constructed, never queried (.files / .empty / .contains / .visit)
# after store+load: create src/file3
```

Not executed on this lab host.
