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

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Cargo Fingerprint Invalidation with `-Zpublic-dependency`

**Environment Context**  
Nightly toolchain: `cargo 1.97.0-nightly (4f9b52075)`, `rustc` with `exported_private_dependencies` lint  
Project structure: `foo` crate exposing `dep::FromDep` in public API  
Prior state: Replicated upstream failure from `ac87f85a9bfe1816fa5d4e805d8182a12d61d047`  

---

### Step 1: Verify Initial State
```bash
cargo clean
cargo -Zpublic-dependency check --message-format=short
```
**Output:**  
```
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.18s
```
**Observation:**  
- Warning appears as expected  
- `target/` directory populated  

---

### Step 2: Trigger Unexpected Behavior
```bash
cargo check --message-format=short
```
**Output:**  
```
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.02s
```
**Anomalies:**  
1. Warning persists despite flag removal  
2. No `[CHECKING] foo` line → No recompilation occurred  
3. Execution time reduced (0.02s vs 0.18s) → Artifact reuse  

---

### Step 3: Inspect Build Artifacts
```bash
ls -l target/debug/.fingerprint/foo-*
```
**Output:**  
```
-rw-r--r-- 1 user group 1675 Feb 15 10:30 dep-fingerprint
-rw-r--r-- 1 user group  142 Feb 15 10:30 dep-lib-foo
```
**Observation:**  
Fingerprint files modified during initial `-Zpublic-dependency` run remain unchanged after second check.  

---

### Step 4: Check Dependency Metadata
```bash
cat target/debug/.fingerprint/foo-*/dep-lib-foo
```
**Output:**  
```
dep:0.1.0
```
**Observation:**  
Dependency tracking file shows only crate name/version. No evidence of `public-dependency` flag state.  

---

### Step 5: Clean and Test Inverse Case
```bash
cargo clean
cargo check --message-format=short
cargo -Zpublic-dependency check --message-format=short
```
**Output (final command):**  
```
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.01s
```
**Anomalies:**  
1. No warning when flag is *added*  
2. No `[CHECKING]` line → No recompilation  
3. Execution time minimal (0.01s) → Artifact reuse  

---

### Step 6: Force Recompilation Attempt
```bash
touch src/lib.rs
cargo -Zpublic-dependency check --message-format=short
```
**Output:**  
```
[COMPILING] foo v0.0.1
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.21s
```
**Observation:**  
- Warning appears after source modification  
- Confirms lint works when compilation occurs  

---

### Key Findings  
1. **Fingerprint Gap**  
   - Toggling `-Zpublic-dependency` doesn't invalidate fingerprints  
   - `target/debug/.fingerprint` files show no change when flag is toggled  

2. **Artifact Reuse Behavior**  
   - Cargo skips recompilation when flag changes  
   - Uses existing artifacts regardless of flag state  

3. **Warning Display Logic**  
   - Warnings reappear if artifacts exist from previous `-Zpublic-dependency` run  
   - Clean builds suppress warnings correctly  

4. **Metadata Shortcoming**  
   - Current fingerprint files (`dep-lib-foo`) track dependency presence but not *how* they're used  
   - No evidence of lint-related flags in fingerprint data  

**Conclusion**  
The core issue is fingerprint invalidation: Cargo's dependency tracking doesn't account for changes in `exported_private_dependencies` lint requirements. The tool treats artifacts as valid across flag-toggling events because:  
- Fingerprints don't encode lint configuration  
- Artifact metadata doesn't record private/public dependency usage  
- Recompilation only triggers on source/dependency version changes  

This creates state-dependent warning behavior tied to build history rather than current flags. The environment requires either:  
1. Manual `cargo clean` between flag changes, or  
2. Fundamental changes to Cargo's fingerprinting of lint configurations  

**Next Action**  
Inspect `cargo` internals for fingerprint composition logic regarding unstable flags... (awaiting further CLI tool exploration)

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
