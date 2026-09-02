// Reduced excerpt of LockfilePackageGraph::populate_packages on failing_ref
// df96f06c70aaba8aa9152afc7726a78101694cdb
// specifiers are written from remaining root_packages.
// jsr.dependencies is the unfiltered BTreeSet.

    for (req, id) in self.root_packages {
      packages.specifiers.insert(req.into_jsr_dep(), value);
    }

    for (id, package) in self.packages {
      match package {
        LockfileGraphPackage::Jsr(package) => {
          packages.jsr.insert(
            ...,
            crate::JsrPackageInfo {
              integrity: package.integrity,
              dependencies: package
                .dependencies
                .into_iter()
                .map(|req| req.into_jsr_dep())
                .collect(),
            },
          );
        }
