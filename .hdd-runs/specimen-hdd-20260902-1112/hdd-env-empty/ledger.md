# HDD Ledger

Iteration: 1

## Preserve

- Empty assignment in a file is not the same event as an unset key
- Different loaders disagree: skip-empty keeps inherited /x; assign stores empty

## Established

- Host-captured fixture output: skip_empty '/x' '2' ; assign '' '2' ; process KEY unset in this run

## Rejected

- envprobe is not installed; attach/simulate/trace output is Dreamer-generated
- The claim that POSIX always turns empty strings into unset is not a specimen fact (Python os.environ can hold empty strings)

## Constraints

- No process attachment, no tracer, no hidden OS oracle
- Only the two loader return dicts and os.environ.get prints are observable

## Open Questions

- (none)

## Human Pressure

- There is no process-attach tracer. Only the two loader return dicts and os.environ prints are observable. Emit a layer table for KEY.

## Harvest Candidates

- For one KEY, show inherited, file text, skip-empty result, assign result, and process env, labeled by layer

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: ask which value won for a key across inherited, file (including empty), loader policy, and process env
Nearest existing operation: printenv plus reading the dotenv file plus reading loader source
Observable delta: one query that distinguishes empty assignment from unset and names the winning layer
Reason: ordinary tools conflate missing and empty; the surviving question is layer provenance of a single key
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no envprobe. Continue only if you can emit the layer table from the two loader functions and os.environ without attaching to a process.

## Pending

(none)
