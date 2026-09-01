You are grounding an HDD exploration after Dreaming has produced useful affordances.

        Do not continue fictional lore. Extract what can be stolen back into reality.
        Treat the latest Red Pen affordance assessment in the ledger as grounding input.
        Do not upgrade the affordance classification merely to make the harvest sound stronger.

        If the latest Red Pen assessment is THIN_WRAPPER or NO_SURVIVOR, preserve that
        conclusion unless the grounded evidence in the supplied record directly contradicts it.

        Do not invent a "Why Existing Tools Are Not Enough" argument when no observable
        delta has been established.

        # Seed

        An unfamiliar developer CLI is already installed in this environment.

Discover it by using it while investigating a bug that only appears after a recent change.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


        # Current Artifact

        ### Field Report: Resolving Runtime Version Conflict  

**Newly Accepted Constraints:**  
- No deployment system or hotfix tracker exists; all changes are local.  
- CLI cannot infer protocol versions; must derive from working tree.  
- Do not invent IDs; use only observed identifiers.  

**Command Attempted:**  
```bash  
dev config source runtime.version  
```  
**Observation:**  
```  
CONFIG SOURCE:  
runtime.version = "3.2" (locked)  
Defined in: .config/overrides.cfg (line 5)  
```  

**Command Attempted:**  
```bash  
dev change inspect --file=.config/overrides.cfg  
```  
**Observation:**  
```  
FILE HISTORY: .config/overrides.cfg  
[No modifications in last 10 changes]  
```  

**Command Attempted:**  
```bash  
dev change inspect --file=runtime/init.js  
```  
**Observation:**  
```  
FILE HISTORY: runtime/init.js  
Change #8821 (2023-10-07 09:15 UTC):  
- version: "3.2" → "3.0" (line 15)  
```  

**Conflict Confirmed:**  
- Hotfix #8821 modified `runtime/init.js` to set version="3.0"  
- Config override forces `runtime.version="3.2"`  
- Test logs show actual runtime initializes as v3.0  

**Command Attempted:**  
```bash  
dev test --suite=runtime --log=live  
```  
**Observation:**  
```  
[LIVE LOG] Runtime initialization:  
Loading runtime/init.js...  
Runtime version: 3.0 (from source)  
[WARN] Config conflict: runtime.version=3.2 ignored  
```  

**Resolution Command:**  
```bash  
dev config unset runtime.version  
```  
**Observation:**  
```  
Success: Removed override for 'runtime.version'  
Active configuration now matches runtime/init.js (v3.0)  
```  

**Verification Command:**  
```bash  
dev test --suite=runtime  
```  
**Observation:**  
```  
Running runtime tests...  
[PASS] Basic execution (0.2s)  
[SKIP] Hybrid mode integration (hybrid_runtime disabled)  
```  

**Conclusion:**  
The locked configuration override conflicted with the runtime's actual version (3.0) set by hotfix #8821. Removing the override resolved the version mismatch and test failure. The environment now consistently reports v3.0 across:  
- Source code (`runtime/init.js`)  
- Runtime initialization  
- Configuration state  

**Recommendation:**  
Audit configuration overrides after local changes to prevent version drift.


        # Ledger

        # HDD Ledger

Iteration: 2

## Preserve

- The session treated environment state, config, and a recent change as comparable objects.
- A conflict was found: config claims runtime 3.2, a test log shows 3.0, status says hybrid runtime disabled.
- dev config source runtime.version named .config/overrides.cfg (line 5) as the declaration site.
- A second file (runtime/init.js) held a different version string than the config key.

## Established

- Commands used: dev status --full, test --suite=runtime, log show, config get, deploy --dry-run.
- Commands: config source, change inspect --file, config unset, test --suite.

## Rejected

- Unsupported precision: v1.5.0, dates 2023-10-05/07, hotfix #8821, protocol 3.2 vs 3.0, log id XR8821-7.
- Hotfix #8821 and timestamps were invented again despite the no-ID constraint.
- Live test logs and config unset as a repair are not required for the mismatch query.

## Constraints

- There is no deployment system, hotfix tracker, or remote runtime in this environment.
- The CLI has no hidden knowledge of protocol versions. It may only compare what a working tree and its recent local changes actually contain.
- Do not invent log IDs or ticket numbers.

## Open Questions

- Can a single non-interactive command answer: what does config declare, what does the tree actually do, and which recent change split them?

## Human Pressure

- (none)

## Harvest Candidates

- Compare declared configuration, observed local behavior, and the change that opened the gap, as one query.
- For a configuration key, show where it is declared and where the tree assigns or implies a different value.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: given a config key, list declaration site(s) and contradicting assignments in the tree
Nearest existing operation: rg the key across config and source, then read both
Observable delta: one query whose result is the disagreement pair, not a search hit list
Reason: primitives are grep/read; the bound question is still worth a small CLI; further dreaming is adding IDs not evidence
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        Produce a grounded harvest with exactly these sections:

        # Core Affordance
        # Affordance Classification
        # Nearest Existing Operation
        # Observable Delta
        # Surviving Abstractions
        # Removed Magic
        # Reality Mapping
        # Research Boundary
        # Smallest Useful Artifact
        # Why Existing Tools Are Not Enough

        Separate directly observable mechanisms from inferred semantics and user-declared semantics.
