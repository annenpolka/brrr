# TASK

Gradle configuration cache can keep the identity of **named files from a previous project location** after the project directory is copied or moved. CC identity omits the build tree root, so a copied `.gradle/configuration-cache` entry is reused. Stored named-file absolute paths still point at the old location.

On failing_ref `e0ca283b48bc739f14140b8a61565d689758c032`, `ConfigurationCacheRepository.Layout.checkFingerprint` registers `rootDirs` as watchable hierarchies and then checks classloader / fingerprint. It does **not** compare `startParameter.buildTreeRootDirectory` against stored `rootDirs`.

Public report (gradle/gradle#36392):

```
gradle init --type java-library --use-defaults
gradle assemble
cp -rf orig copy
# modify a source file in copy
echo broken > lib/src/main/java/org/example/Library.java
cd copy && gradle assemble
```

```
BUILD SUCCESSFUL
Configuration cache entry reused.
```

UP-TO-DATE looks at leftover named source files in `orig`, not `copy`.

In-tree after the repair (not on failing_ref): if `buildTreeRootDirectory !in rootDirs`, return `CheckedFingerprint.Invalid` ("the location of the build has changed from … to …"). Tests copy and move.

Case A — second `gradle assemble` in the original directory:
  CC load is the same location
  named-file paths still match
  not leftover-after-relocate

Case B — copy/move the project including `.gradle/configuration-cache`, then assemble:
  leftover: CC entry + named-file absolute paths from the previous location
  build location omitted from CC identity
  UP-TO-DATE on leftover orig files

Case C — delete `.gradle/configuration-cache` in the copy then assemble:
  fresh CC identity
  not leftover named files from orig

Case D — location included in CC identity (post-repair shape, not on failing_ref):
  "cannot be reused because the location of the build has changed"
  not leftover named-file paths

The developer wants to know which identity case B actually used for named source files: leftover orig absolute paths, copy's current paths, or omitted (no CC entry).
