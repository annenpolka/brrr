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
