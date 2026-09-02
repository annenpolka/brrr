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

        ### Field Report: Investigating Cache-Control Divergence in Django Middleware

**Operator Log:**  
Executing within Django environment (commit cd7554e5517992d5ca2594ffc936cb193daab26c). Focused on cache middleware behavior with `no-store` vs `private` directives.

---

### Step 1: Reproduce Issue with Test Extension  
Added test case to `tests/cache/tests.py` to verify `no-store` behavior under middleware stack:

```python
def test_cached_control_no_store_not_cached(self):
    """Responses with 'Cache-Control: no-store' should not be cached."""
    # Define view with no-store header
    def no_store_view(request, unique):
        resp = HttpResponse(f"Test {unique}")
        resp["Cache-Control"] = "no-store"
        return resp

    # Apply middleware stack directly (not via cache_page decorator)
    handler = self.build_middleware_chain(
        no_store_view,
        middleware_classes=[
            UpdateCacheMiddleware,
            CommonMiddleware,
            FetchFromCacheMiddleware
        ]
    )

    # First request
    request = self.factory.get("/no-store/")
    response1 = handler(request, "A")
    self.assertEqual(response1.content, b"Test A")

    # Second request (same URL)
    response2 = handler(request, "B")
    self.assertEqual(response2.content, b"Test B")  # Expect fresh response
```

**Command:**  
`python tests/runtests.py cache.CacheMiddlewareTest.test_cached_control_no_store_not_cached --verbosity=2`

**Output:**  
```
test_cached_control_no_store_not_cached (cache.tests.CacheMiddlewareTest) ... FAIL
======================================================================
FAIL: test_cached_control_no_store_not_cached (cache.tests.CacheMiddlewareTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/.../tests/cache/tests.py", line [X], in test_cached_control_no_store_not_cached
    self.assertEqual(response2.content, b"Test B")
AssertionError: b'Test A' != b'Test B'
```

**Observation:**  
Test fails. Second request returns cached `Test A` despite `no-store` header. Confirms ticket behavior.

---

### Step 2: Trace Middleware Flow  
Inspected middleware execution path using debug logging:

**Modified `django/middleware/cache.py`:**  
Added trace points in `UpdateCacheMiddleware.process_response`:

```python
class UpdateCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        print(f"UpdateCache: Checking response for caching | Status: {response.status_code} | CC: {response.get('Cache-Control')}")

        # ... existing checks ...

        if "private" in response.get("Cache-Control", ()):
            print("UpdateCache: Skipping cache (private directive)")
            return response

        # ... caching logic ...
        print(f"UpdateCache: Caching response (key: {cache_key})")
        return response
```

**Command:**  
Re-ran test with tracing

**Output:**  
```
UpdateCache: Checking response for caching | Status: 200 | CC: no-store
UpdateCache: Caching response (key: views.decorators.cache.cache_page....GET....)
```

**Observation:**  
`UpdateCacheMiddleware` ignores `no-store` directive. Only checks for `private`. Response cached despite `no-store`.

---

### Step 3: Verify Fetch Middleware Behavior  
Added trace to `FetchFromCacheMiddleware.process_request`:

```python
class FetchFromCacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        cache_key = self.get_cache_key(request)
        print(f"FetchFromCache: Checking cache for key {cache_key}")
        response = self.cache.get(cache_key)
        if response:
            print("FetchFromCache: Serving cached response")
        return response
```

**Output During Second Request:**  
```
FetchFromCache: Checking cache for key views.decorators.cache.cache_page....GET....
FetchFromCache: Serving cached response
```

**Observation:**  
Fetch middleware serves cached response before view executes. Bypasses view entirely.

---

### Step 4: Compare with Private Directive  
Re-ran existing `test_cached_control_private_not_cached` with tracing:

**Output:**  
```
UpdateCache: Checking response for caching | Status: 200 | CC: private
UpdateCache: Skipping cache (private directive)
```

**Observation:**  
`private` correctly bypasses caching due to explicit check in `UpdateCacheMiddleware`. `no-store` lacks equivalent handling.

---

### Key Findings  

| Directive | Middleware Handling | Cached? |
|-----------|---------------------|---------|
| `private` | Explicit skip in `UpdateCacheMiddleware` | ❌ |
| `no-store` | No special handling; cached normally | ✅ |

**Divergence Cause:**  
- `UpdateCacheMiddleware` contains hardcoded check for `private` ([code](django/middleware/cache.py))  
- No equivalent check for `no-store` or `no-cache` directives  
- Fetch middleware honors cached entries regardless of original `Cache-Control`  

**Second Request Source:**  
Serving cached response from `FetchFromCacheMiddleware` using cache key generated during first request. View never executed.

**Recommended Code Change:**  
Extend `UpdateCacheMiddleware` check to include `no-store` and `no-cache`:
```python
if any(directive in response.get("Cache-Control", "") 
       for directive in ("private", "no-store", "no-cache")):
    return response
```

**Environment Note:**  
All observations made within Django test framework. No external tools used beyond provided test runner.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
