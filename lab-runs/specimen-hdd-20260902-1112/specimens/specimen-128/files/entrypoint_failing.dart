// Reduced excerpt of isLockFileUpToDate + mapping check on failing_ref
// lib/src/entrypoint.dart
// 425174668513d0696a637e62c683ec5885999914
// Missing workspace members are omitted from identity.

      if (!root.immediateDependencies.values.every(isDependencyUpToDate)) {
        final pubspecPath = p.normalize(p.join(dir, 'pubspec.yaml'));
        log.fine(
          'The $pubspecPath file has changed since the $lockFilePath file '
          'was generated.',
        );
        return false;
      }

      bool isPackagePathsMappingUpToDateWithLockfile(
        Map<String, String> packagePathsMapping, {
        required String lockFilePath,
        required String packageConfigPath,
      }) {
        // extra mappings only — missing workspace packages omitted
        final hasExtraMappings =
            !packagePathsMapping.keys.every((packageName) {
              return workspaceRoot.transitiveWorkspace.any(
                    (p) => p.name == packageName,
                  ) ||
                  lockFile.packages.containsKey(packageName);
            });
        if (hasExtraMappings) {
          return false;
        }
        return lockFile.packages.values.every((lockFileId) {
          final packagePath = packagePathsMapping[lockFileId.name];
          return packagePath != null;
        });
      }
