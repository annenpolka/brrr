repository: swiftlang/swift-package-manager
issue: https://github.com/swiftlang/swift-package-manager/issues/8981
pr: https://github.com/swiftlang/swift-package-manager/pull/9144
cherry_pick_pr: https://github.com/swiftlang/swift-package-manager/pull/9210
failing_ref (squash parent of 9144 on main): d8ae00bc06a6c5f643d5b843537a8118766c3c7c
fixed_ref (squash merge of 9144): 1abd9a2f87e568fdfa67bd4564cea65872aaeaac
cherry_pick_base (release/6.2): 0da281d271f090f4d61e4182e8584f36a8026e26
cherry_pick_head: ae39ccbcb8e8a14263a197c2825c8d4d5811c7d7
merged_at: 2025-09-29T21:43:54Z
pr_author: ZachNagengast
merged_by: plemarquand
changed_files: Sources/PackageRegistry/RegistryClient.swift, Tests/PackageRegistryTests/RegistryClientTests.swift
pr_title: Fix inverted logic on registry cache expiration
scout_note: not specimen-075/086/115. Distinct leftover: inverted TTL + MetadataCacheKey omits version so leftover checksum fingerprint is stored for a new version. Cherry-pick PR 9210 is the same repair on release/6.2.
