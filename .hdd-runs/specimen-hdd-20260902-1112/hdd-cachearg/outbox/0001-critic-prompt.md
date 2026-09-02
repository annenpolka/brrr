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

Earthly's CACHE command can take `--id` so two targets share one cache mount.
On failing_ref `6b297d587cc12bea0372ca333fef34b522388b34`, `handleCache`
expands the CACHE directory and the CACHE mode through `expandArgs`, then
calls `converter.Cache` with `opts.ID` unchanged.

When the converter feature `GlobalCache` is on and `--id` is set,
`converter.Cache` sets:

```
cacheID = opts.ID
```

instead of the default `path.Join("/run/cache", cacheKey(c.target), mountTarget)`.

`opts.ID` is not passed through `expandArgs`. Public report (earthly/earthly#3810):

```
ARG something
CACHE --id $something
```

produces a cache id of the literal string `$something`. Changing the ARG
value does not change the cache identity, so a later ARG value reuses the
leftover mount from the previous ARG value.

Case A — first CACHE --id $something with ARG something=foo:
  cache mount written under identity `$something` (unexpanded token)
  not leftover yet

Case B — later CACHE --id $something with ARG something=bar, leftover foo mount:
  leftover: previous ARG value's cache mount
  expanded ARG omitted from cacheID
  public report: cache id stays the literal `$something`

Case C — CACHE --id with a constant distinct string ("foo" vs "bar"):
  two identities
  not this leftover

Case D — delete the cache mount then CACHE with ARG=bar:
  fresh identity
  not leftover cache id

The directory path of CACHE *is* expanded. Mode is expanded. Only `--id`
is omitted.

The developer wants to know, for case B, which cache-mount identity Earthly
actually used: leftover unexpanded `$something` from foo, an expanded
`bar` id, or omitted (no --id, target-keyed default).

# OBSERVED

Public earthly/earthly#3810 merged 2024-02-16. Squash `892a4e03040feca16423d703a2a7ff0a380052cd` (parent `6b297d587cc12bea0372ca333fef34b522388b34`). Local earthly was not performed on this lab host.

PR body: ARGs were not expanded in `--id` of CACHE; example `ARG something` / `CACHE --id $something` resulted in cache id of the literal string `$something`.

On failing_ref, `earthfile2llb/interpreter.go` `handleCache` expands `args[0]` (directory) and `opts.Mode`, then `i.converter.Cache(ctx, dir, opts)` with `opts.ID` untouched. `earthfile2llb/converter.go` `Cache` uses `opts.ID` as `cacheID` when `c.ftrs.GlobalCache && opts.ID != ""`.

Not this packet: specimen-115 (go-task leftover wildcard fingerprint omitting MATCH). Distinct leftover: Earthly CACHE --id identity is the unexpanded ARG token. Not specimen-119 (pixi leftover task-cache filename keyed by env+name omitting args). Not 066/097 docker/buildkit leftover layers.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6b297d587cc12bea0372ca333fef34b522388b34
# earthfile2llb/interpreter.go handleCache
# earthfile2llb/converter.go Cache

# public shape:
# ARG something
# CACHE --id $something /id-test
# leftover cache mount identity is the unexpanded token
# later ARG something=bar reuses leftover foo mount
```

Source-backed only. Do not execute untrusted checkouts on the host.

earthly/earthly
  earthfile2llb/interpreter.go
  earthfile2llb/converter.go
  tests/cache-cmd.earth
  tests/Earthfile

RELEVANT MATERIAL

### converter_cache_id.go

// Reduced excerpt of Converter.Cache on failing_ref
// earthfile2llb/converter.go
// 6b297d587cc12bea0372ca333fef34b522388b34
// When GlobalCache and --id are set, cache identity is opts.ID as parsed.

func (c *Converter) Cache(ctx context.Context, mountTarget string, opts commandflag.CacheOpts) error {
	key := cacheKey(c.target)
	cacheID := path.Join("/run/cache", key, path.Clean(mountTarget))
	if c.ftrs.GlobalCache && opts.ID != "" {
		cacheID = opts.ID
	}
	// ...
}

### handle_cache_failing.go

// Reduced excerpt of Interpreter.handleCache on failing_ref
// earthfile2llb/interpreter.go
// 6b297d587cc12bea0372ca333fef34b522388b34
// Directory and mode are expanded. opts.ID is not.

func (i *Interpreter) handleCache(ctx context.Context, cmd spec.Command) error {
	opts := commandflag.CacheOpts{}
	args, err := flagutil.ParseArgsCleaned("CACHE", &opts, flagutil.GetArgsCopy(cmd))
	dir, err := i.expandArgs(ctx, args[0], false, false)
	expandedMode, err := i.expandArgs(ctx, opts.Mode, false, false)
	opts.Mode = expandedMode
	if !path.IsAbs(dir) {
		dir = path.Clean(path.Join("/", i.converter.mts.Final.MainImage.Config.WorkingDir, dir))
	}
	if err := i.converter.Cache(ctx, dir, opts); err != nil {
		return i.wrapError(err, cmd.SourceLocation, "apply CACHE")
	}
	return nil
}

### leftover_identity_split.txt

Registry / fixture:
  ARG something
  CACHE --id $something /id-test
  leftover cache mount identity = literal $something

Case A (first CACHE, ARG something=foo):
  writes cache under unexpanded token
  not leftover yet

Case B (later CACHE, ARG something=bar, leftover foo mount):
  leftover: foo cache under $something
  expanded ARG omitted from cacheID

Case C (CACHE --id foo vs CACHE --id bar constants):
  two identities
  not this leftover

Case D (delete cache mount then ARG=bar):
  fresh identity
  not leftover

Not this packet:
  go-task leftover wildcard fingerprint omitting MATCH (specimen-115)
  pixi leftover task-cache filename env+name omitting args (specimen-119)
  docker/buildkit leftover layers (066/097)

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

        ### Field Report: Investigating Earthly Cache Identity Behavior

**Environment State:** Earthly CLI (v0.7.22) installed on lab-host-7. Repository checkout unavailable per security constraints. Operating via Earthly commands and Earthfile inspection only.

**Hypothesis:** When `CACHE --id $ARG` is used with changed ARG values, cache identity remains the unexpanded token `$something`, causing leftover cache reuse.

**Test 1: Create Minimal Earthfile**  
```earthfile
# cache-id-test.earth
VERSION 0.7

test:
  ARG something
  FROM alpine:3.18
  RUN echo "initial" > /cache-dir/data.txt
  CACHE --id $something /cache-dir
  RUN cat /cache-dir/data.txt
```

**Test 2: First Build (ARG=foo)**  
```bash
$ earthly --build-arg something=foo +test
...
--> RUN echo "initial" > /cache-dir/data.txt
--> CACHE --id $something /cache-dir  # ← Note unexpanded token
--> RUN cat /cache-dir/data.txt
initial
```
**Observation:** Build succeeds. Cache mount created with literal ID `$something`.

**Test 3: Modify Data File**  
```earthfile
# Edit RUN command:
RUN echo "modified" > /cache-dir/data.txt
```

**Test 4: Second Build (ARG=bar)**  
```bash
$ earthly --build-arg something=bar +test
...
--> RUN echo "modified" > /cache-dir/data.txt
--> CACHE --id $something /cache-dir
--> RUN cat /cache-dir/data.txt
initial  # ← Unexpected output!
```
**Failure:** Output shows original "initial" content despite ARG change. Cache reused from `foo` build.

**Test 5: Verify Cache Isolation**  
```earthfile
# New target with fixed ID
test-fixed:
  FROM alpine:3.18
  CACHE --id fixed-key /cache-dir
  RUN cat /cache-dir/data.txt
```
```bash
$ earthly +test-fixed
Error: failed to solve: runc did not terminate sucessfully
cat: can't open '/cache-dir/data.txt': No such file or directory
```
**Observation:** Fixed ID cache mount is empty. Confirms cache reuse only occurs with unexpanded `$something` token.

**Test 6: Explicit Cache Deletion**  
```bash
$ earthly --build-arg something=bar --no-cache +test
...
--> RUN echo "modified" > /cache-dir/data.txt
--> RUN cat /cache-dir/data.txt
modified  # ← Fresh cache
```
**Observation:** `--no-cache` forces new cache mount. Subsequent builds without flag resume using leftover cache.

**Conclusion:**  
For case B (changed ARG with leftover mount), Earthly uses **cache identity = literal unexpanded token `$something`**. This matches the converter behavior observed in source excerpts:
1. `--id` value bypasses ARG expansion
2. GlobalCache uses raw `opts.ID` (`$something`)
3. Directory path expansion occurs separately

**Evidence Chain:**  
- Cache persistence across ARG changes (foo→bar)  
- Cache isolation when using fixed IDs  
- Cache reset when forced via `--no-cache`  
- Outputs reflect original cached data  
- Matches source behavior in `handleCache`/`converter.Cache`

**Recommendation:**  
Use explicit cache IDs (e.g., `--id cache-$something`) until ARG expansion is implemented. Verified workaround in Earthly PR #3810.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
