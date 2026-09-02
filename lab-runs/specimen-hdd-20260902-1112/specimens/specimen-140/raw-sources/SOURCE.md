repository: microsoft/rushstack
issue: https://github.com/microsoft/rushstack/issues/4400
pr: https://github.com/microsoft/rushstack/pull/4476
failing_ref (parent of merge on main): 300fcd107dea176ef503ffa073776bff47ee17a1
fixed_ref (operation-graph cache hashes): 3530cb21a03927ec8b06072ee89a91466dc6beb3
merged_at: 2024-10-17T20:13:49Z
pr_author: dmichon-msft
merged_by: iclanton
changed_files: ProjectBuildCache.ts, CacheableOperationPlugin.ts, InputsSnapshot.ts, ProjectChangeAnalyzer.ts, others
pr_title: [rush] Split ProjectChangeAnalyzer, fix build cache hashes
scout_note: not 136 pants process cache. not 134 moon .env. Distinct leftover: npm project-dep walk omits operation-graph inputs so leftover downstream phase cache stayed current. unique vs 001-139.
