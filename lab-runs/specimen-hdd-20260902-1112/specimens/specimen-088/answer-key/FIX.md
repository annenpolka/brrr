KNOWN FIX (sealed): gradle/gradle PR 23265 merge e4355b87b8ffc775cc005724853a10f95b1a58c8.

ConfigurableFileTree query methods (getFiles, isEmpty, contains, visit) did not notify configuration-cache input tracking, so a directory tree read at configuration time never became WorkInputs in the fingerprint. Adding src/file3 after a store reused the entry. Repair: FileCollectionObservationListener on the file-collection factory; DefaultConfigurableFileTree/FileTreeAdapter query methods call fileCollectionObserved before walking; ConfigurationCacheFingerprintWriter implements that listener and writes WorkInputs + host.fingerprintOf. Fixed integration test then misses with "an input to build file 'build.gradle' has changed" and prints files=[file1, file2, file3]. Fixed-name files() still does not treat element contents as configuration inputs.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
