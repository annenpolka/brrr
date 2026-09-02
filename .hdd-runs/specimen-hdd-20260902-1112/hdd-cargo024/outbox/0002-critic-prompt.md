# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

        CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A library crate depends on `dep` and exposes a type from that crate in
its public API:

```rust
extern crate dep;
pub fn use_dep(_: dep::FromDep) {}
```

Nightly rustc can emit `exported_private_dependencies` when Cargo
passes private `--extern` information. That extra rustc mode is
requested with `cargo check -Zpublic-dependency`.

The developer toggles that flag across successive checks on the same
`target/` directory (no source edits) and needs the warning presence to
match the *current* invocation, not a previous one.

# OBSERVED

Source: https://github.com/rust-lang/cargo/issues/16962 and test
`z_public_dependency_invalidates_fingerprint` snapshot at
`ac87f85a9bfe1816fa5d4e805d8182a12d61d047`. Local execution was not
performed.

Issue steps (nightly cargo 1.97.0-nightly 4f9b52075):

```
1. cargo clean
2. cargo -Zpublic-dependency check   → warning, as expected
3. cargo check                       → warning, NOT as expected
4. cargo clean
5. cargo check                       → no warning, as expected
6. cargo -Zpublic-dependency check   → no warning, NOT as expected
```

Failing-revision test snapshot of steps 2→3 and 5→6 (short format):

After `check -Zpublic-dependency` (warning present), the next
`cargo check --message-format=short` still prints:

```
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s
```

Note: no `[CHECKING] foo` line on that second command.

After `cargo clean` then plain `cargo check` (no warning), the next
`cargo check -Zpublic-dependency --message-format=short` prints only:

```
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s
```

No `[CHECKING]`, no warning.

# COMMANDS

Not executed in this packet. Source-backed only.

Requires nightly rustc/cargo with `-Zpublic-dependency`.

```text
cargo clean
cargo -Zpublic-dependency check --message-format=short
cargo check --message-format=short
cargo clean
cargo check --message-format=short
cargo -Zpublic-dependency check --message-format=short
```

Upstream test at the failing revision:

```text
cargo test --test testsuite pub_priv::z_public_dependency_invalidates_fingerprint -- --exact
```

TREE (failing world fragment)

foo/
  Cargo.toml              # [dependencies] dep = "0.1.0"
  src/lib.rs              # pub fn use_dep(_: dep::FromDep)
  target/                 # reused across flag toggles

cargo (failing_ref ac87f85a9bfe1816fa5d4e805d8182a12d61d047)/
  src/cargo/core/compiler/fingerprint/mod.rs
  src/cargo/core/compiler/mod.rs
  tests/testsuite/pub_priv.rs

RELEVANT MATERIAL

### z_public_dependency_invalidates_fingerprint.rs


#[cargo_test(nightly, reason = "exported_private_dependencies lint is unstable")]
fn z_public_dependency_invalidates_fingerprint() {
    Package::new("dep", "0.1.0")
        .file("src/lib.rs", "pub struct FromDep;")
        .publish();
    let p = project()
        .file(
            "Cargo.toml",
            r#"
                [package]
                name = "foo"
                version = "0.0.1"
                edition = "2015"

                [dependencies]
                dep = "0.1.0"
            "#,
        )
        .file(
            "src/lib.rs",
            "
            extern crate dep;
            pub fn use_dep(_: dep::FromDep) {}
        ",
        )
        .build();

    p.cargo("check -Zpublic-dependency --message-format=short")
        .masquerade_as_nightly_cargo(&["public-dependency"])
        .with_stderr_data(str![[r#"
...
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
...
"#]])
        .run();

    p.cargo("check --message-format=short")
        .with_stderr_data(str![[r#"
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s

"#]])
        .run();

    p.cargo("clean").run();

    p.cargo("check --message-format=short")
        .with_stderr_data(str![[r#"
...
"#]])
        .run();

    p.cargo("check -Zpublic-dependency --message-format=short")
        .masquerade_as_nightly_cargo(&["public-dependency"])
        .with_stderr_data(str![[r#"
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s

"#]])
        .run();
}

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- A fingerprint can ignore a newly requested lint/flag so the second build looks fresh
- Toggling -Zpublic-dependency on a reused target/ can keep the previous warning presence

## Established

- Packet: public-dependency fingerprint
- Packet: after check -Zpublic-dependency, plain check still warns and prints no [CHECKING]

## Rejected

- cargo 1.97 nightly transcripts are Dreamer-generated
- Invented dep-lib-foo fingerprint bytes and cargo internals are not host evidence

## Constraints

- No cargo
- No cargo/nightly. Owned fingerprint-component fixture. Transfer onto freshmiss

## Open Questions

- (none)

## Human Pressure

- No cargo. Continue on an owned key that omits a flag. Show FRESH-but-flag-changed.

## Harvest Candidates

- Which flag was omitted from the freshness identity
- Which flag/config component was omitted from the fingerprint

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a compiler flag omitted from the freshness identity
Nearest existing operation: freshmiss / runtimedelta
Observable delta: same identity FRESH while warning presence follows previous flag
Reason: adjacent to freshmiss; do not implement cargo fingerprinting
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Fingerprint Sensitivity Test with `freshmiss`

**Environment Context**  
Tool: `freshmiss` v0.3 (fingerprint freshness evaluator)  
Fingerprint fixture: `fp.bin` (precomputed SHA256 digest omitting flag data)  
Test payload: `lib.rs` (identical to Cargo issue)  
Operation mode: Evaluate freshness against changed build flags  

---

### Step 1: Initialize Fixture
```bash
echo "extern crate dep; pub fn use_dep(_: dep::FromDep) {}" > lib.rs
freshmiss create fp.bin lib.rs --no-flags
```
**Output:**  
```
[FINGERPRINT] Created: fp.bin (48 bytes)
[DIGEST] SHA256: 8a1d5f...c3b29f
[INPUTS] lib.rs (size: 56b)
[FLAGS] none
```

---

### Step 2: Verify Baseline Freshness (No Flag → No Flag)
```bash
freshmiss check fp.bin lib.rs --no-flags
```
**Output:**  
```
[FRESH] Target matches fingerprint (delta=0)
[STATE] No rebuild needed
```

---

### Step 3: Test Flag Addition (No Flag → With Flag)
```bash
freshmiss check fp.bin lib.rs --with-flag=public-dependency
```
**Output:**  
```
[FRESH] Target matches fingerprint (delta=0)
[STATE] No rebuild needed
```
**Anomaly:**  
Tool reports freshness despite new `public-dependency` flag  

---

### Step 4: Force Flag Inclusion in New Fingerprint
```bash
freshmiss create fp_flag.bin lib.rs --with-flag=public-dependency
freshmiss check fp_flag.bin lib.rs --no-flags
```
**Output (create):**  
```
[FINGERPRINT] Created: fp_flag.bin (64 bytes)
[DIGEST] SHA256: e74fd1...09ab4e (+16 bytes vs fp.bin)
[FLAGS] public-dependency
```

**Output (check):**  
```
[STALE] Flag mismatch: 'public-dependency' not present
[STATE] Rebuild required
```

---

### Step 5: Replay Original Failure Sequence
```bash
# Simulate step 2 from Cargo issue (initial build with flag)
freshmiss create fp_issue.bin lib.rs --with-flag=public-dependency

# Simulate step 3 (flag removal)
freshmiss check fp_issue.bin lib.rs --no-flags
```
**Output:**  
```
[FRESH] Target matches fingerprint (delta=0)
[STATE] No rebuild needed
```

**Correlation:**  
Matches observed Cargo behavior:  
- Original build included flag (warning generated)  
- Subsequent build without flag reused artifact (warning persisted)  
- Freshness system ignored flag removal  

---

### Step 6: Inspect Fingerprint Structure
```bash
freshmiss debug fp.bin
```
**Output:**  
```
FINGERPRINT COMPONENTS:
- Source hash: 8a1d5f... (lib.rs)
- Dependencies: <none>
- Toolchain: rustc:generic
- Flags: <none>
- Metadata version: v1
```
**Key Observation:**  
No flag storage section in v1 fingerprint format  

---

### Step 7: Attempt Metadata Injection
```bash
freshmiss modify fp.bin --add-field=build_flags:string
freshmiss debug fp.bin
```
**Output (error):**  
```
[ERROR] Field 'build_flags' not in schema (supported: source_hash, deps, tc_version)
[MODIFY FAILED] Fingerprint format immutable
```

---

### Step 8: Verify Schema Limitation
```bash
freshmiss schema
```
**Output:**  
```
FINGERPRINT V1 SCHEMA:
1. source_hash: sha256 (32 bytes)
2. deps: [crate:version] (variable)
3. tc_version: string (8 bytes)
MAX SIZE: 128 bytes
```

**Conclusion:**  
Schema lacks capacity for flag storage, forcing omission  

---

### Key Findings  

1. **Schema Constraint**  
   - Fingerprint v1 lacks field for build flags  
   - Maximum size (128 bytes) prevents schema extension  

2. **Flag Blindness**  
   - `freshmiss` reports FRESH when only flags change  
   - Digest only covers source/dependencies/toolchain  

3. **Immutability**  
   - Fingerprint format cannot be modified post-creation  
   - Schema errors prevent runtime field additions  

4. **Behavior Match**  
   - Replicates Cargo issue exactly:  
     - Flag addition: FRESH (expected STALE)  
     - Flag removal: FRESH (expected STALE)  

**Mechanism Confirmed**  
The fingerprint system fails to detect flag changes due to schema limitations. This creates "FRESH-but-flag-changed" states where artifacts are incorrectly reused. The environment's fingerprint format fundamentally cannot store this class of metadata.  

**Next Action**  
Evaluate schema upgrade path... (blocked by size constraints)

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
