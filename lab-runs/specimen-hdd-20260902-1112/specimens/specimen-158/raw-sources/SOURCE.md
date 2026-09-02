repository: microsoft/vcpkg-tool
issue: https://github.com/microsoft/vcpkg-tool/pull/1997
pr: https://github.com/microsoft/vcpkg-tool/pull/1997
related_pr: https://github.com/microsoft/vcpkg-tool/pull/1988
failing_ref (parent of squash on main): e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
fixed_ref (Windows empty vs unset split): 643c71f3626a7820e48c51d11545711a594dad02
merged_at: 2026-05-12T20:12:07Z
pr_author: BillyONeal
merged_by: BillyONeal
changed_files: include/vcpkg/base/system.h, src/vcpkg/base/system.cpp, src/vcpkg-test/system.cpp, src/vcpkg/binarycaching.cpp, src/vcpkg/commands.build.cpp, src/vcpkg/commands.edit.cpp, src/vcpkg/commands.integrate.cpp, src/vcpkg/vcpkgcmdarguments.cpp, src/vcpkg/visualstudio.cpp, src/vcpkg-test/util.cpp
pr_title: Fix empty vs. unset environment variables on Windows.
scout_note: not 010/031/149/150. leftover unset after empty FOO= JOIN on Windows GetEnvironmentVariableW sz==0. unique vs 001-155.
