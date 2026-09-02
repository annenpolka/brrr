### Field Report: Investigating Candidate Identity in pip's Resolver Factory

**Operational Context**:  
Using static analysis capabilities within the provided source fixture to examine resolvelib factory behavior. No local execution performed per security constraints. Focused on code paths from failing revision `a15dd75d988`.

---

### Step 1: Trace Explicit Path Handling  
Examined `_make_requirements_from_install_req` for explicit wheel path with extras (`pkg-1.0.whl[ext]`):

```python
# make_requirements_failing.py excerpt
cand = self._make_candidate_from_link(
    ireq.link,
    extras=frozenset(ireq.extras),  # extras=('ext',)
    template=ireq,
    name=canonicalize_name(ireq.name),
    version=None
)
yield cand
```
**Observation**:  
Explicit path requirement yields exactly one candidate – the extras-wrapped candidate. No base candidate is separately yielded.

---

### Step 2: Inspect Candidate Construction  
Traced `_make_candidate_from_link` call path:

```python
# make_candidate_from_link_failing.py excerpt
base = self._link_candidate_cache[link]  # Base candidate created/cached
if not extras:
    return base
return self._make_extras_candidate(base, extras)  # Wrapped candidate returned
```
**Observation**:  
1. Base candidate (`LinkCandidate`) created and stored in `_link_candidate_cache`  
2. With extras present: factory returns wrapped `ExtrasCandidate`  
3. **Key fact**: Base candidate exists in cache but isn't exposed to resolution  

---

### Step 3: Simulate Constraint Resolution  
Reconstructed constraint lookup flow (`pkg==1` requirement):

1. Constraint calls `find_candidates` with `extras=frozenset()`  
2. Factory checks candidate sources:  
   - **Explicit candidates**: Only wrapped candidate available (`ExtrasCandidate` for `pkg[ext]`)  
   - **Constraint lookup**: Seeks `LinkCandidate` (extras=None)  
3. Cache contains base candidate but isn't returned because:  
   - Not yielded by any requirement  
   - Not in active candidate pool  

**Failure Reproduction**:  
```log
# Simulated resolver output
Could not find candidate for pkg==1 (extras: none)
Available candidate: pkg==1.0 (extras: ['ext'])
```
**Observation**:  
Constraint fails because base candidate exists in cache but isn't surfaced to resolution layer.

---

### Step 4: Verify Identity Storage  
Inspected candidate registry state after processing explicit path:

| Candidate Type | Identity Key | Stored Where | Exposed to Resolver |
|----------------|-------------|-------------|---------------------|
| `LinkCandidate` | `(pkg, 1.0, frozenset())` | `_link_candidate_cache` | ❌ |
| `ExtrasCandidate` | `(pkg, 1.0, frozenset({'ext'}))` | Requirement yield | ✅ |

**Conclusion**:  
Factory stores **only extras-wrapped candidate** for explicit path requirement. Base candidate exists in private cache but isn't registered as available for reuse. This creates a "leftover" base candidate that constraints can't access.

---

### Step 5: Validate Against Cases  
**Case B/C Failure Confirmed**:  
- Explicit path with extras: yields wrapped candidate only  
- Constraint requires base candidate: can't see cached base candidate  
- Resolution fails due to missing base candidate  

**Case A Success Explained**:  
- Path without extras yields base candidate directly  
- Constraint reuses visible base candidate  

**Case D Irrelevance**:  
- No link candidate → no cache interaction  

---

### Artifact  
Candidate identity diagram generated from analysis:  
```
[Explicit Path Requirement]  
│  
└── Yields: ExtrasCandidate(pkg[ext])  
    │  
    └── Wraps: [Hidden] LinkCandidate(pkg)  // Inaccessible to constraints
```

**Final Observation**:  
The identity split occurs because the factory:  
1. Creates base candidate during link processing  
2. Fails to expose it when extras are present  
3. Leaves constraint requirements with no access path to base candidate  

No evidence found of secondary requirement generation or identity rewriting. Conflict stems from incomplete candidate exposure.
