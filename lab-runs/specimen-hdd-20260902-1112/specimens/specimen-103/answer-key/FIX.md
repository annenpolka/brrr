KNOWN FIX (sealed): golang/go CL 762602 submitted 8191cd88683192e9aa3f3a1c11e841f8f40a9a9d.

failing_ref is CL first parent a2214422293d2c26ad389050f25460b3f2f00825.

Workspace graph used workspace replaces; EnterModule then forced those versions under each module's own replaces. Hidden requirements made workspace versions lower. EditBuildList conflicted; continue left leftover go.mod.

CL repair: addReq additive EditBuildList(loader, ctx, addFor[m], nil); Fatal on error; UpdateGoModFromReqs then write after ExitIfErrors. work_sync_replace.txt: a keeps quote v1.0.0 under replace; b without replace gets quote v1.1.0.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
