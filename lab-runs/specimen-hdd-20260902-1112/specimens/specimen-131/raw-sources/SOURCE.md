repository: ninja-build/ninja
issue: https://github.com/ninja-build/ninja/issues/2666
pr: https://github.com/ninja-build/ninja/pull/2680
failing_ref (merge first parent on master): 77d328f5f679bfef14b1f67f3cd431b729bc786f
fixed_ref (merge commit): 88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68
merged_at: 2026-07-19T12:17:57Z
pr_author: moritzx22
merged_by: jhasse
changed_files: src/graph.cc, src/graph.h, src/graph_test.cc, src/build_test.cc, src/build_log.cc, src/build_log.h, src/disk_interface_test.cc, src/missing_deps.cc
pr_title: Only load depsfile if not dirty [Fix #2666]
scout_note: not 075/086. Distinct leftover: ninja deps-log identity loaded when producing edge is dirty so leftover previous dep graph remains after sources flip. job-0558.
