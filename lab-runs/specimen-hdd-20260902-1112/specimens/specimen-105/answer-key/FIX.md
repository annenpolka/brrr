KNOWN FIX (sealed): denoland/deno_lockfile PR 62 merge 3ef94bed3135eeae91515f8451a67de62094fe34.

failing_ref is squash parent df96f06c70aaba8aa9152afc7726a78101694cdb.

populate_packages serialized jsr.dependencies from the unfiltered BTreeSet after remove_root_pkg_by_id had already dropped shared npm specifiers from root_packages.

PR repair: populate specifiers after packages; filter jsr.dependencies with root_packages.contains_key(dep). Spec test remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
