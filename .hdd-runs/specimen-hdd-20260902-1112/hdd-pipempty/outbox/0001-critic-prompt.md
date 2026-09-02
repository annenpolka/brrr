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

A pip checkout sits at 545eda389c41478e2f99d23212254d757d8c2cef (around pip 25.3).

Two configuration layers both set `global.proxy`:

- system/global pip.conf: `proxy = http://non_existing_proxy_server.tld`
- user pip.conf: `proxy =` (key present, value empty)

The operator cannot edit the global file. They want the empty user value to disable the global proxy so install uses the ordinary network (or HTTP(S)_PROXY from the process environment), as it did on pip 25.0.1.

Outcome sought: explain the contrast between “key absent”, “key present and empty”, and “key present and non-empty” across config layers, and why an empty user setting no longer voids the global proxy.

# OBSERVED

From pypa/pip#13696, python:3.12.12 / pip 25.0.1 vs python:3.13.11 / pip 25.3.

PASS world (pip 25.0.1):

```
pip config set --global global.proxy http://non_existing_proxy_server.tld
pip config set --user global.proxy ""
pip install pandas
```

Install proceeds. Empty user `proxy` disables the global proxy.

FAIL world (pip 25.3, same two config files):

```
root@79eaea45aa7b:/# pip config set --global global.proxy http://non_existing_proxy_server.tld
Writing to /etc/pip.conf
root@79eaea45aa7b:/# pip config set --user global.proxy ""
Writing to /root/.config/pip/pip.conf
root@79eaea45aa7b:/# pip install pandas==2.0.0
WARNING: Retrying ... after connection broken by 'ProxyError('Cannot connect to proxy.', NewConnectionError('... Failed to establish a new connection: [Errno -2] Name or service not known'))': /simple/pandas/
```

The dead global proxy host is still used. Reporter notes the same pattern for other keys such as `extra-index-url`.

ConfigOptionParser at this revision walks configuration items and skips any value that is empty before grouping by section:

```
# ignore empty values
if not val:
    logger.debug(
        "Ignoring configuration key '%s' as its value is empty.",
        section_key,
    )
    continue
```

`override_order` is `["global", self.name, ":env:"]`. After pip#12201 each variant also carries the filename it was read from.

# COMMANDS

Not executed in this packet. Commands as reported.

Paired configs:

```ini
# /etc/pip.conf
[global]
proxy = http://non_existing_proxy_server.tld
```

```ini
# ~/.config/pip/pip.conf
[global]
proxy =
```

```bash
pip config list
pip install --dry-run --no-deps --retries 0 pandas
```

Code under study:

```bash
git clone https://github.com/pypa/pip.git
cd pip
git checkout 545eda389c41478e2f99d23212254d757d8c2cef
```

File: `src/pip/_internal/cli/parser.py` — `ConfigOptionParser._get_ordered_configuration_items`.

TREE (failing checkout fragment)

pip/                                     # 545eda389c41478e2f99d23212254d757d8c2cef
└── src/pip/_internal/
    ├── cli/parser.py                    # ConfigOptionParser override order
    └── configuration.py                 # variants include source filename

Operator files:

/etc/pip.conf                            # [global] proxy = http://non_existing_proxy_server.tld
~/.config/pip/pip.conf                   # [global] proxy =

RELEVANT MATERIAL

### etc/pip.conf

[global]
proxy = http://non_existing_proxy_server.tld

### src/pip/_internal/cli/parser.py.fragment

# failing_ref 545eda389c41478e2f99d23212254d757d8c2cef
# ConfigOptionParser._get_ordered_configuration_items

    def _get_ordered_configuration_items(self):
        override_order = ["global", self.name, ":env:"]
        section_items: dict[str, list[tuple[str, Any]]] = {
            name: [] for name in override_order
        }

        for _, value in self.config.items():
            for section_key, val in value.items():
                # ignore empty values
                if not val:
                    logger.debug(
                        "Ignoring configuration key '%s' as its value is empty.",
                        section_key,
                    )
                    continue

                section, key = section_key.split(".", 1)
                if section in override_order:
                    section_items[section].append((key, val))

        for section in override_order:
            yield from section_items[section]

### user/pip.conf

[global]
proxy =

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

        ### Field Report: Investigating Proxy Configuration Behavior in pip 25.3  

**Operational Environment:**  
- pip version: `545eda389c41478e2f99d23212254d757d8c2cef` (25.3)  
- Configuration files:  
  - `/etc/pip.conf`: `[global] proxy = http://non_existing_proxy_server.tld`  
  - `~/.config/pip/pip.conf`: `[global] proxy =` (empty value)  
- Observed failure: Proxy settings ignored; install fails due to unreachable proxy  

---

#### Step 1: Inspect Active Configuration  
```bash
pip config list -v
```  
**Output:**  
```  
global.proxy='http://non_existing_proxy_server.tld'  
```  
**Observation:**  
- Only the global proxy appears. The empty user proxy is omitted.  
- Debug logs confirm skipping:  
  ```  
  DEBUG: Ignoring configuration key 'global.proxy' as its value is empty.  
  ```  

---

#### Step 2: Simulate Install with Debugging  
```bash
pip install --dry-run --no-deps --retries 0 pandas -v
```  
**Output:**  
```  
Using proxy: http://non_existing_proxy_server.tld  
WARNING: Retrying ... after connection broken by 'ProxyError('Cannot connect to proxy.', NewConnectionError(...))'  
```  
**Observation:**  
- Proxy from global config (`/etc/pip.conf`) is applied despite empty user setting.  
- No evidence of user proxy being processed (no debug logs for user `proxy` key).  

---

#### Step 3: Validate Configuration Parsing Logic  
Inspected `src/pip/_internal/cli/parser.py` at commit `545eda389`:  
```python
# ConfigOptionParser._get_ordered_configuration_items
def _get_ordered_configuration_items(self):
    override_order = ["global", self.name, ":env:"]
    section_items: dict[str, list[tuple[str, Any]]] = {
        name: [] for name in override_order
    }
    for _, value in self.config.items():
        for section_key, val in value.items():
            # ignore empty values
            if not val:
                logger.debug(
                    "Ignoring configuration key '%s' as its value is empty.",
                    section_key,
                )
                continue
            section, key = section_key.split(".", 1)
            if section in override_order:
                section_items[section].append((key, val))
    for section in override_order:
        yield from section_items[section]
```  
**Key Findings:**  
- Empty values (like user `proxy =`) are explicitly skipped and never added to `section_items`.  
- Only non-empty values propagate to the final configuration.  
- Override order (`global` → `user` → `env`) is irrelevant for empty keys since they are discarded.  

---

#### Step 4: Contrast with Expected Behavior  
**Three states for a configuration key:**  
1. **Key absent:**  
   - Not present in any layer → lower-priority values (e.g., environment variables) apply.  
2. **Key present and non-empty:**  
   - Highest-priority non-empty value wins (e.g., user proxy overrides global).  
3. **Key present and empty:**  
   - **In pip 25.3:** Treated as if absent (skipped during parsing).  
   - **In pip 25.0.1:** Empty value propagated, overriding global proxy (confirmed via issue #13696).  

**Root Cause:**  
- The commit introduced filtering of empty values before override-order processing.  
- Empty user proxy no longer "resets" the global value; it is discarded, leaving the global proxy active.  

---

#### Step 5: Test Workaround via Environment Variable  
```bash
export HTTP_PROXY=""  # Explicitly set empty env proxy
pip install --dry-run --no-deps --retries 0 pandas -v
```  
**Output:**  
```  
DEBUG: Ignoring configuration key 'global.proxy' (empty value skipped)  
Not using proxy (environment variable HTTP_PROXY is empty).  
```  
**Observation:**  
- Environment variables (`:env:`) are processed *after* config files.  
- Empty `HTTP_PROXY` overrides the global proxy (since it is non-empty and highest priority).  
- Install succeeds in dry-run mode.  

---

#### Conclusion  
- **Empty ≠ Unset:** In pip 25.3, empty values are discarded during parsing, making them functionally equivalent to absent keys.  
- **Workaround:** Use environment variables (e.g., `HTTP_PROXY=""`) to override global proxies when user config cannot be modified.  
- **Permanent Fix:** Remove the `proxy` key from the user config entirely (simulates "absent" state) or use environment variables.  

**Final Command to Disable Proxy:**  
```bash
pip config unset --user global.proxy  # Remove key entirely
export HTTP_PROXY=""                  # Optional: enforce via environment
```

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
