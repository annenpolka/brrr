# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

An unfamiliar developer CLI is already installed in this environment.

Discover it by using it after an automated coding assistant changed the tree and the result needs to be understood.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

### Field Report: Re-examining Changes with Observable Constraints  

**Current State**:  
Working directory unchanged from prior report. `.dxstate` manifest present. CLI `dx` remains operational.  

---  

#### Step 1: Verify CLI command constraints  
Re-ran help with focus on `resolve` parameters:  
```bash  
./dx resolve --help  
```  
**Output**:  
```  
resolve - Explain changes via observable artifacts  

USAGE:  
  resolve --target=PATH [--with-context]  

REQUIRES:  
  Changes must be reflected in:  
    - Code comments containing RFC 2119 keywords (MUST, SHOULD, etc)  
    - Git commit messages (if VCS baseline available)  
    - Markdown decision logs (*.decision.md)  
```  
**Discovery**:  
- `resolve` depends exclusively on *present* artifacts  
- No external vulnerability/ticket integration  

#### Step 2: Re-attempt config change rationale  
Ran resolve against config.yaml with context flag:  
```bash  
./dx resolve --target=config.yaml --with-context  
```  
**Output**:  
```  
No supported rationale artifacts found for config.yaml:  
  - Missing: SECURITY.decision.md  
  - Missing: commit message metadata  
```  
**Failure Analysis**:  
- CLI requires explicit decision documentation  
- Automated assistant left no observable rationale  

#### Step 3: Inspect code changes directly  
Used `trace` to extract modified function context:  
```bash  
./dx trace --file=src/main.py --diff  
```  
**Output**:  
```  
--- src/main.py (pre-assistant)  
+++ src/main.py (current)  
@@ -42,7 +42,7 @@  
- def validate_input(data):  
-     # DEPRECATED: Use security_scanner instead  
-     return basic_check(data)  
+  
+ def security_scanner(data):  
+     # Implements validation RFC v3  
+     return advanced_check(data, level=config.security_level)  
```  
**Observation**:  
- Removal of `validate_input()` accompanied by deprecation comment  
- New `security_scanner()` references RFC (unverified)  

#### Step 4: Validate RFC reference  
Searched working tree for RFC documentation:  
```bash  
find . -name '*rfc*.md'  
```  
**Output**:  
```  
./docs/validation_rfc_v3.md  
```  
**Inspection**:  
```bash  
cat ./docs/validation_rfc_v3.md  
```  
**Relevant Excerpt**:  
```markdown  
## Section 4.1: Backward Compatibility  
SHOULD provide legacy wrappers unless:  
- Security constraints prohibit compatibility (MUST justify in SECURITY.decision.md)  
```  
**Discovery**:  
- RFC exists but requires companion security decision log  
- No `SECURITY.decision.md` found in project  

---  

**Findings**:  
1. `resolve` command fails without explicit decision artifacts  
2. Deprecation comment suggests planned obsolescence  
3. RFC v3 mandates backward-compatibility wrappers *unless* security-justified  
4. Critical gap: Missing `SECURITY.decision.md` for override justification  

**Next Actions**:  
- Reconstruct security constraint from test changes: `./dx trace --file=tests/security_scanner_test.py --diff`  
- Check for residual decision artifacts: `find . -name '*.decision.*'`  

**Unresolved**:  
Why does `config.security_level` increase break compatibility? (No observable link between config change and RFC)

## Behavior already demonstrated

- The operator's problem was a working tree changed by an automated assistant.
- trace listed file-level modifications; resolve was asked to explain a config change.
- resolve refused to invent intent when no rationale artifacts were present.
- trace --diff showed a removed function whose remaining docs/RFC required a companion decision file that was absent.
- Commands: dx --help, state, trace --init, trace --source=auto, resolve --target, config, trace --dependencies.
- resolve --help lists required artifact classes; resolve --target=config.yaml --with-context reported missing SECURITY.decision.md; find located docs/validation_rfc_v3.md.


## Newly confirmed limits and corrections

- Invented CVE-2024-1234, GHSA-abc1-xyz9, ticket SEC-789, libseccheck 3.1.0→3.2.1, and timestamps.
- resolve claimed to know mitigation rationale that is not present in the working tree as shown.
- The RFC file and RFC 2119 contract look like they were created to satisfy the tool's own newly stated requirements; they were not shown to pre-exist independently of this session.
- There is no hidden assistant transcript, ticket tracker, or vulnerability database.
- The CLI cannot invent why a change happened. It may only observe the working tree, diffs, and files actually present.
- Do not require a .dxstate manifest as magical prior knowledge; if a baseline is needed, it must be something the operator can see.
- The CLI has no private catalog of required artifacts and no RFC 2119 special mode unless those words actually occur in files.
- Do not create missing decision logs. Report absence.
- Operate on a real git diff in a real tree.


## New information since the previous report

- There is no private policy language. Continue on a real git diff in this repository.
- The CLI must not write decision files. If an obligation is missing, say so and stop.
- Show concrete file:line evidence for each claimed obligation.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
