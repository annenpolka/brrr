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

A Django checkout sits at cd7554e5517992d5ca2594ffc936cb193daab26c.

Site cache is enabled with the documented two-part middleware order:

```python
MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]
```

A view returns an `HttpResponse` whose `Cache-Control` is `no-store` and whose body includes `datetime.datetime.now()`. A second GET to the same URL still returns the first timestamp.

A related path uses the `cache_page` decorator (built from `CacheMiddleware`, which subclasses both update and fetch classes). Existing tests show `Cache-Control: private` is not stored. `no-store` / `no-cache` were not in that test.

Outcome sought: why `private` and `no-store` diverge under this middleware pair, and what the second request is actually serving.

# OBSERVED

Django ticket 36560, Django 5.2.

settings excerpt:

```
MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]
```

views.py:

```python
from django.http import HttpResponse
import datetime

def cache_demo(request):
    resp = HttpResponse(f"Current content at {datetime.datetime.now()}")
    resp["Cache-Control"] = "no-store"
    return resp
```

Reported: when Cache-Control is `no-store`, the response content is still cached. A later request shows the earlier clock string.

`UpdateCacheMiddleware.process_response` at this revision (after streaming/status/cookie checks):

```python
        # Don't cache a response with 'Cache-Control: private'
        if "private" in response.get("Cache-Control", ()):
            return response
```

Paired unit test already in the tree (`tests/cache/tests.py`):

```python
    def test_cached_control_private_not_cached(self):
        # Responses with Cache-Control: private are not cached.
        view_with_private_cache = cache_page(3)(
            cache_control(private=True)(hello_world_view)
        )
        request = self.factory.get("/view/")
        response = view_with_private_cache(request, "1")
        self.assertEqual(response.content, b"Hello World 1")
        response = view_with_private_cache(request, "2")
        self.assertEqual(response.content, b"Hello World 2")
```

That test passes. The ticket's `no-store` view does not behave the same way: request 2 still looks like request 1.

`cache_page` is `decorator_from_middleware` around `CacheMiddleware`. `CacheMiddleware` inherits `UpdateCacheMiddleware.process_response`. Fetch middleware is last on the request; update middleware is first on the list so it runs last on the response.

# COMMANDS

Not executed in this packet. Commands as reported / as they would be in Django's cache tests.

```bash
git clone https://github.com/django/django.git
cd django
git checkout cd7554e5517992d5ca2594ffc936cb193daab26c
```

Relevant files:

- `django/middleware/cache.py`
- `tests/cache/tests.py` (`test_cached_control_private_not_cached`, `test_cache_page_timeout`)
- ticket reproducer view with `Cache-Control: no-store`

Focused test module (full Django test run is large):

```bash
python tests/runtests.py cache --verbosity=2
```

Ticket reproducer: run the view twice under the two-part cache middleware and compare bodies.

TREE (failing checkout fragment)

django/                                  # cd7554e5517992d5ca2594ffc936cb193daab26c
├── django/
│   ├── middleware/cache.py              # UpdateCacheMiddleware, FetchFromCacheMiddleware, CacheMiddleware
│   └── views/decorators/cache.py        # cache_page, cache_control, never_cache
└── tests/cache/tests.py

Ticket world:

settings.py                              # UpdateCacheMiddleware first, FetchFromCacheMiddleware last
views.py                                 # Cache-Control: no-store, body includes now()

RELEVANT MATERIAL

### django/middleware/cache.py.fragment

# failing_ref cd7554e5517992d5ca2594ffc936cb193daab26c
# UpdateCacheMiddleware.process_response (excerpt)

        if response.streaming or response.status_code not in (200, 304):
            return response

        if (
            not request.COOKIES
            and response.cookies
            and has_vary_header(response, "Cookie")
        ):
            return response

        # Don't cache a response with 'Cache-Control: private'
        if "private" in response.get("Cache-Control", ()):
            return response

        timeout = self.page_timeout
        if timeout is None:
            timeout = get_max_age(response)
            if timeout is None:
                timeout = self.cache_timeout
            elif timeout == 0:
                return response
        patch_response_headers(response, timeout)
        if timeout and response.status_code == 200:
            cache_key = learn_cache_key(
                request, response, timeout, self.key_prefix, cache=self.cache
            )
            if hasattr(response, "render") and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)
                )
            else:
                self.cache.set(cache_key, response, timeout)
        return response

### settings_middleware.py

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

### tests/cache/tests.py.fragment

# failing_ref cd7554e5517992d5ca2594ffc936cb193daab26c

    def test_cached_control_private_not_cached(self):
        """Responses with 'Cache-Control: private' are not cached."""
        view_with_private_cache = cache_page(3)(
            cache_control(private=True)(hello_world_view)
        )
        request = self.factory.get("/view/")
        response = view_with_private_cache(request, "1")
        self.assertEqual(response.content, b"Hello World 1")
        response = view_with_private_cache(request, "2")
        self.assertEqual(response.content, b"Hello World 2")

### views.py

from django.http import HttpResponse
import datetime

def cache_demo(request):
    resp = HttpResponse(f"Current content at {datetime.datetime.now()}")
    resp["Cache-Control"] = "no-store"
    return resp

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

- Cache-Control private can be treated as non-storeable while no-store is still stored
- A second GET can serve the first timestamp despite no-store

## Established

- Packet: UpdateCache + FetchFromCache; view Cache-Control no-store plus datetime.now(); second GET same timestamp; private already tested not stored

## Rejected

- Django test runner output and invented timestamps are not host evidence
- A recommended middleware patch is not a specimen observation

## Constraints

- No Django checkout
- An owned store-policy table (private/no-store/no-cache) is the world

## Open Questions

- (none)

## Human Pressure

- No Django. Continue on the owned cache_page.py fixture only. Show which pipeline stage was frozen in the cached object.

## Harvest Candidates

- Ask which Cache-Control tokens prevent store, and what the second request actually served

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: for a response, name which cache-control tokens blocked store vs which were ignored, and whether the second GET was a cache hit
Nearest existing operation: read Cache-Control and compare two response bodies
Observable delta: one query that treats private-vs-no-store store policy as the object
Reason: identical timestamps look like a slow clock; the remainder is store policy
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no Django. Continue only on an owned cache-control token fixture.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Cache-Control Token Fixture Operation

**Operational Context:**  
Working within owned cache-control token fixture (private, no-store, no-cache). Pipeline stages modeled as:  
1. Request ingress  
2. Cache lookup  
3. View processing  
4. Cache storage decision  
5. Response egress  

**Commands Executed:**  

```python
# Initialize token processor
from cache_fixture import Pipeline

# Create pipeline with instrumentation
p = Pipeline(
    stages=['ingress', 'cache_lookup', 'view', 'storage_decision', 'egress'],
    capture_state=['headers', 'body_fragment', 'cache_status']
)

# Test case 1: 'private' token
print("=== RUN private ===")
p.reset()
p.set_token('private')
p.run_request()
state1 = p.capture_state()
p.run_request()
state2 = p.capture_state()

# Test case 2: 'no-store' token
print("\n=== RUN no-store ===")
p.reset()
p.set_token('no-store')
p.run_request()
state3 = p.capture_state()
p.run_request()
state4 = p.capture_state()

# Output captured states
print("\nSTATE CAPTURE:")
print(f"private@req1: {state1}")
print(f"private@req2: {state2}")
print(f"no-store@req1: {state3}")
print(f"no-store@req2: {state4}")

# Inspect frozen stage
print("\nFROZEN OBJECT INSPECTION:")
if state4['cache_status'] == 'HIT':
    frozen_obj = p.get_cached_object('/test')
    print(f"Storage stage: {frozen_obj['frozen_at_stage']}")
    print(f"Headers: {frozen_obj['headers']}")
    print(f"Body pattern: {frozen_obj['body_fragment']}")
```

**Output:**  
```
=== RUN private ===
[ingress] HEADER: Cache-Control: private
[cache_lookup] MISS (no valid object)
[view] Generating new content: ts=2024-06-15T14:30:22.123456
[storage_decision] SKIPPED (private token)
[egress] Sending: Cache-Control: private

[ingress] HEADER: Cache-Control: private
[cache_lookup] MISS (no valid object)
[view] Generating new content: ts=2024-06-15T14:30:23.654321
[storage_decision] SKIPPED (private token)
[egress] Sending: Cache-Control: private

=== RUN no-store ===
[ingress] HEADER: Cache-Control: no-store
[cache_lookup] MISS (no valid object)
[view] Generating new content: ts=2024-06-15T14:30:24.987654
[storage_decision] STORING (no-store not blocked)
[egress] Sending: Cache-Control: no-store

[ingress] HEADER: Cache-Control: no-store
[cache_lookup] HIT (valid object found)
[egress] Sending: Cache-Control: no-store

STATE CAPTURE:
private@req1: {'headers': {'Cache-Control': 'private'}, 'body_fragment': 'ts=2024-06-15T14:30:22.123456', 'cache_status': 'MISS'}
private@req2: {'headers': {'Cache-Control': 'private'}, 'body_fragment': 'ts=2024-06-15T14:30:23.654321', 'cache_status': 'MISS'}
no-store@req1: {'headers': {'Cache-Control': 'no-store'}, 'body_fragment': 'ts=2024-06-15T14:30:24.987654', 'cache_status': 'STORED'}
no-store@req2: {'headers': {'Cache-Control': 'no-store'}, 'body_fragment': 'ts=2024-06-15T14:30:24.987654', 'cache_status': 'HIT'}

FROZEN OBJECT INSPECTION:
Storage stage: storage_decision
Headers: {'Cache-Control': 'no-store', 'Content-Type': 'text/plain'}
Body pattern: 'ts=2024-06-15T14:30:24.987654'
```

**Key Observations:**  
1. **Token Handling Divergence**  
   - `private` token triggers storage bypass at `storage_decision` stage  
   - `no-store` token passes through storage decision unimpeded  

2. **Cache Object Provenance**  
   Frozen object contains complete response snapshot captured at **storage_decision** stage:  
   - Includes original `no-store` header  
   - Contains view-generated timestamp  
   - Preserves all headers/body from processing completion  

3. **Request 2 Behavior**  
   For `no-store` path:  
   - Cache lookup returns full frozen object  
   - Pipeline short-circuits after cache hit  
   - Original `no-store` header and timestamp served verbatim  

**Failure Reproduction:**  
```python
# Verify frozen header contradiction
cached = p.get_cached_object('/test')
print(f"Cached header vs served: {cached['headers']['Cache-Control'] == 'no-store'}")  # True
print(f"Header instructs not to store, but stored anyway")  # Explicit contradiction
```

**Conclusion:**  
The divergence occurs because:  
- `private` token is handled at **storage_decision** stage (prevents caching)  
- `no-store` token is only interpreted by clients, not enforced by cache infrastructure  
- Frozen object captures the exact response state at **storage_decision** pipeline stage  
- Subsequent requests serve the cached object with its original `no-store` header intact  

This explains why the second request returns the original timestamp despite the `no-store` directive - the cache stores and replays the complete response, including the contradictory header.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
