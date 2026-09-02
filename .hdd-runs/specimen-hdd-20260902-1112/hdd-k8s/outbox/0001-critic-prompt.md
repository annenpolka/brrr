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

`kubectl wait` documents `--timeout` as: zero means check once and do not wait. After a recent change, waiting on an already-existing Deployment with `--timeout=0` does not perform that one-shot check.

A typical invocation:

```
kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=0
```

returns an error about `--wait-for-creation` instead of `deployment.apps/test-3 condition met` (or a one-shot condition failure).

The developer wants to know which default now governs timeout 0, whether the object is even visited, and how that interacts with the flag help text.

# OBSERVED

Public kubernetes/kubernetes#125630 (revert of behavior from #122994) on failing merge parent `50f27d9ef496fe69da6d2969134df6dd2f9aa9b3`.

Flag help still says: `Zero means check once and don't wait, negative means wait for a week.`

On this revision `NewWaitFlags` sets `WaitForCreation: true` by default. `RunWait` begins with:

```
if o.WaitForCreation && o.Timeout == 0 {
    return fmt.Errorf("--wait-for-creation requires a timeout value greater than 0")
}
```

So `--timeout=0` errors before the condition function runs, even when the object already exists.

`--wait-for-creation` help: `The default value is true. If set to true, also wait for creation of objects if they do not already exist. This flag is ignored in --for=delete`.

#122994 release note (later cleared): `kubectl wait` will now wait for resources to be created by default.

# COMMANDS

```
git checkout 50f27d9ef496fe69da6d2969134df6dd2f9aa9b3
# against a cluster with deploy/test-3 already present:
kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=0
```

Expected on older wait semantics: one-shot check, `condition met` if the jsonpath is already populated. Observed on this revision: error requiring `--wait-for-creation` timeout greater than 0.

This packet does not start a cluster. Treat the wait.go excerpt and the command error as the world.

kubernetes/kubernetes @ 50f27d9ef496fe69da6d2969134df6dd2f9aa9b3
  staging/src/k8s.io/kubectl/pkg/cmd/wait/wait.go
  test/cmd/wait.sh
  test/cmd/legacy-script.sh

RELEVANT MATERIAL

### staging/src/k8s.io/kubectl/pkg/cmd/wait/wait.go.excerpt

// excerpt @ 50f27d9ef496fe69da6d2969134df6dd2f9aa9b3
// staging/src/k8s.io/kubectl/pkg/cmd/wait/wait.go

type WaitFlags struct {
	RESTClientGetter     genericclioptions.RESTClientGetter
	PrintFlags           *genericclioptions.PrintFlags
	ResourceBuilderFlags *genericclioptions.ResourceBuilderFlags
	Timeout         time.Duration
	ForCondition    string
	WaitForCreation bool
	genericiooptions.IOStreams
}

func NewWaitFlags(...) *WaitFlags {
	return &WaitFlags{
		// ...
		Timeout:         30 * time.Second,
		WaitForCreation: true,
	}
}

func (flags *WaitFlags) AddFlags(cmd *cobra.Command) {
	cmd.Flags().DurationVar(&flags.Timeout, "timeout", flags.Timeout,
		"The length of time to wait before giving up.  Zero means check once and don't wait, negative means wait for a week.")
	cmd.Flags().BoolVar(&flags.WaitForCreation, "wait-for-creation", flags.WaitForCreation,
		"The default value is true. If set to true, also wait for creation of objects if they do not already exist. This flag is ignored in --for=delete")
}

func (o *WaitOptions) RunWait() error {
	ctx, cancel := watchtools.ContextWithOptionalTimeout(context.Background(), o.Timeout)
	defer cancel()

	isForDelete := strings.ToLower(o.ForCondition) == "delete"
	if o.WaitForCreation && o.Timeout == 0 {
		return fmt.Errorf("--wait-for-creation requires a timeout value greater than 0")
	}

	if o.WaitForCreation && !isForDelete {
		err := func() error {
			for {
				select {
				case <-ctx.Done():
					return fmt.Errorf("context deadline is exceeded while waiting for the creation of the resources")
				default:
					err := o.ResourceFinder.Do().Visit(func(info *resource.Info, err error) error {
						return nil
					})
					if err == nil {
						return nil
					}
					if !apierrors.IsNotFound(err) {
						return err
					}
				}
			}
		}()
		if err != nil {
			return err
		}
	}
	// ... condition visit ...
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

        ### Field Report: Investigating `kubectl wait` Behavior at Revision `50f27d9ef`

#### Initial Observation
Ran the specified command against the cluster with an existing `deploy/test-3`:
```bash
kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=0
```
**Output**:  
`error: --wait-for-creation requires a timeout value greater than 0`  
*No indication of object inspection or condition evaluation occurred.*

---

#### Hypothesis Testing
Based on the `wait.go` logic:
1. `WaitForCreation=true` is default  
2. Timeout=0 triggers early error if `WaitForCreation=true`  
3. `--for=delete` ignores `WaitForCreation` (per help text)

**Test 1: Disable creation wait**  
```bash
kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=0 --wait-for-creation=false
```
**Output**:  
`deployment.apps/test-3 condition met`  
*(Confirms one-shot evaluation when bypassing creation check)*  

**Test 2: Verify delete condition exception**  
```bash
kubectl wait --for=delete deploy/test-3 --timeout=0
```
**Output**:  
`deployment.apps/test-3 condition met`  
*(Creation flag ignored as documented, immediate check performed)*  

**Test 3: Negative timeout (bypasses creation check)**  
```bash
kubectl wait --for=jsonpath='{.status.replicas}' deploy/test-3 --timeout=-1s
```
**Output**:  
`deployment.apps/test-3 condition met`  
*(Long timeout allowed with default WaitForCreation=true)*  

---

#### Key Findings
| Parameter Combination              | Result                     | Object Visited? |
|------------------------------------|----------------------------|-----------------|
| `--timeout=0` (default flags)      | Immediate error            | ❌ No           |
| `--timeout=0 --wait-for-creation=false` | One-shot evaluation   | ✅ Yes          |
| `--timeout=0 --for=delete`         | One-shot evaluation   | ✅ Yes          |
| `--timeout=-1s` (default flags)    | Waits indefinitely    | ✅ Yes          |

1. **Governance of Timeout 0**:  
   The default `--wait-for-creation=true` now overrides timeout=0 semantics. The error triggers before resource lookup when both are active.

2. **Object Visibility**:  
   Resources are **not visited** when the early error triggers. Object inspection only occurs when either:  
   - `--wait-for-creation=false` is explicitly set  
   - `--for=delete` is used (disables creation check)  
   - Timeout is >0 or negative  

3. **Help Text Conflict**:  
   The `--timeout` help ("Zero means check once") remains technically correct but is **contextually incomplete**:  
   - Applies only when `--wait-for-creation=false` or `--for=delete`  
   - Undocumented dependency on creation flag creates behavioral ambiguity  

---

#### Recommended Workflow
For one-shot checks on existing resources:
```bash
kubectl wait --for=condition=Available deploy/example --timeout=0 --wait-for-creation=false
```
For deletion checks (preserves original timeout=0 behavior):
```bash
kubectl wait --for=delete deploy/example --timeout=0
```

---

#### Environmental Notes
- Behavior observed at commit `50f27d9ef` (post-#122994)  
- Help text inconsistency confirmed in current `wait.go`  
- Creation wait loop never reached when timeout=0 due to early exit  
- No observed quantum effects or hidden orchestration in code path

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
