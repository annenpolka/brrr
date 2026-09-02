## Field Report: Investigating Omitted Git Identity in Worktree Cache Key

### Situation Recap
We have a fixture representing a linked Git worktree environment where:
- `.git` is a file pointing to worktree metadata
- Main repository holds packed refs
- Cache key records `"commit": null` despite HEAD movement
- Regular clone behaves similarly after `git pack-refs`

### Concrete Operation: Inspecting Fixture Identity Components

**1. Fixture Structure Verification**
```bash
# Navigate to worktree directory
cd /path/to/worktree

# Confirm .git file existence and content
cat .git
```
```text
gitdir: /path/to/main/.git/worktrees/worktree
```

**2. Worktree Metadata Inspection**
```bash
# Examine worktree HEAD
cat /path/to/main/.git/worktrees/worktree/HEAD
```
```text
ref: refs/heads/main
```

**3. Reference Resolution Path**
```bash
# Check for loose ref in worktree metadata
ls /path/to/main/.git/worktrees/worktree/refs/heads
```
```text
ls: cannot access '/path/to/main/.git/worktrees/worktree/refs/heads': No such file or directory
```

**4. Main Repository Packed Refs**
```bash
# Inspect main repository ref storage
cat /path/to/main/.git/packed-refs
```
```text
c3aff6510123456789012345678901234567890 refs/heads/main
deadbeef0123456789012345678901234567890 refs/tags/v0.1.0
```

**5. Commondir Pointer**
```bash
# Check worktree commondir reference
cat /path/to/main/.git/worktrees/worktree/commondir
```
```text
../../..
```

### Key Observation: Omitted Identity
The resolution path failed to access `refs/heads/main` because:
1. Worktree metadata directory lacks loose refs
2. Reference exists only in main repository's `packed-refs`
3. Current implementation doesn't traverse to commondir

### Identity Resolution Failure Path
```
[Worktree Project] 
  → .git (file) 
  → Worktree Metadata (/main/.git/worktrees/worktree)
  → HEAD ("ref: refs/heads/main")
  → Attempt: refs/heads/main (in worktree metadata) ❌ MISSING
```

### Required Resolution Path
```
[Worktree Project] 
  → .git (file) 
  → Worktree Metadata 
  → commondir ("../../..") 
  → Main Repository (.git) 
  → packed-refs ✅ FOUND
```

### Failure Confirmation
The packed reference `c3aff651...` for `refs/heads/main` exists in the main repository but wasn't accessed. This specific identity component was omitted during cache key generation because:
- Reference resolution stopped at worktree metadata directory
- Packed refs in commondir weren't consulted
- No fallback to main repository storage

### Consequence
Cache invalidation depends on detecting HEAD changes, but without accessing the packed ref containing the actual commit SHA, the tool cannot:
1. Record current commit in cache key
2. Detect commit SHA changes during subsequent runs
3. Trigger rebuilds when worktree HEAD moves

**Final Observation:** The packed reference in the commondir-linked main repository is the critical omitted identity component causing cache invalidation failure in linked worktrees.
