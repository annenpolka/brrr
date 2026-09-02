# HDD Ledger

Iteration: 2

## Preserve

- Rewritten assertion failure messages can disagree with values a plain assertion (or the interpreter) computed
- A later assignment-expression can make an earlier operand display the post-assignment value
- Rewritten assertion failure messages can disagree with values a plain assertion computed
- User-visible counters can distinguish live evaluation from a later display re-invocation

## Established

- Packet observation: rewritten explanation showed (False and False) while side_effect returns True
- Packet observation: --assert=plain is a real pytest switch; any output from it in this transcript is unverified Dreamer text
- Packet: rewritten explanation showed (False and False) while side_effect returns True
- Owned specimen-015 replay.py already shows after_eval vs after_explain counts

## Rejected

- Invented rewrite_dump.log / PYTEST_DEBUG bytecode is not specimen evidence
- Precise instruction listings are unsupported precision
- Failure text containing DISPLAY_1 / DISPLAY_2 was not captured on this host
- A display_helper on __builtins__ is not present
- Advice to rewrite tests is not the harvested operation
- A newly invented pytest module with context='live'|'display' is not specimen evidence

## Constraints

- No rewriter bytecode dump, no hidden AST inspector, no semantic oracle
- Only pytest stdout/stderr and user-visible counters may be treated as observable
- No rewriter bytecode dump, no hidden AST inspector
- Only pytest stdout/stderr and user-visible counters in source may be treated as observable
- Grounding must use specimen-015 / pytest stdout, not a fictional context argument inside side_effect

## Open Questions

- Can eval-count vs display-count be shown without inspecting rewriter internals?

## Human Pressure

- This environment cannot dump rewritten bytecode or AST. A companion fixture exists where a display helper re-invokes the expression after the real evaluation. Use the same tool on both. Show which numbers came from the live call versus the display path.

## Harvest Candidates

- Ask which assertion-failure values came from live evaluation versus the display path
- Label each count as live vs display

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show which side-effect counts came from live evaluation versus a display/re-invoke path
Nearest existing operation: print counters in the test plus pytest -s
Observable delta: one report that names the two paths instead of a single incrementing counter
Reason: the remainder is provenance of counts, not a new pytest rewriter
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
