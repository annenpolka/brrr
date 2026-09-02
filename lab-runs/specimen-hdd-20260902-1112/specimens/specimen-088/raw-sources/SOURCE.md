repository: gradle/gradle
pr: https://github.com/gradle/gradle/pull/23265
issue: none (PR-only; related sample gradle/configuration-cache-build-logic-inputs)
failing_ref (merge first parent): 040aac7031d900c2c548154fcbc75627b01e386c
fixed_ref (merge commit): e4355b87b8ffc775cc005724853a10f95b1a58c8
head_sha: 607ec95683b6f29d420b0d8b147e1ee603b2a787
merged_at: 2022-12-22T06:54:24Z
merged_by: bot-gradle
milestone: 8.1 RC1
author: adammurdoch
pr_title: Include any directory queried via ConfigurableFileTree at configuration time in configuration cache fingerprint
changed_paths_note: DefaultConfigurableFileTree query methods, FileCollectionObservationListener, ConfigurationCacheFingerprintWriter, ConfigurationCacheFileCollectionIntegrationTest
scout_note: job-0319 gradle CC file collection identity. Distinct from specimen-076 unusedfp Honor-KILL (system property snapshot), specimen-042 HashMap race, specimen-051 nested ValueSource deadlock. Cargo sealed 086; yarn scout may race 087+.
