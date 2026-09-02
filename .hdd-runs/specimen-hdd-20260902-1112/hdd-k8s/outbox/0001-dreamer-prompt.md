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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
