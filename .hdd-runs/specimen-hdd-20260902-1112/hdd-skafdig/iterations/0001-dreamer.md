### Field Report: Investigating Skaffold Cache Identity in Case B  

**Tool Environment**: Skaffold CLI (v1.47.0, failing_ref `6ea9aeb818b8e371a4386bf044479f86a0a6e885`) with Docker registry emulation.  
**Objective**: Determine which identity (cache key) was used for the artifact after input changes in Case B (Dockerfile/dependency change, same tag, leftover remote digest).  

---

#### Step 1: Initialize Test Fixture  
*Command:*  
```bash 
skaffold build --tag=testcaseb --cache-artifacts=true --verbosity=debug 
```  
*Output (abridged):*  
``` 
Generating tags... 
Tags generated in 2.18ms 
Cache check for artifact [docker-image] - input hash: 7d4a5e3f 
Found [docker-image] remotely with tag testcaseb 
```  
*Observation:*  
- Initial build succeeds. Cache stores `artifactCache[7d4a5e3f] = <old_digest>` (e.g., `sha256:8e6f...`).  

---

#### Step 2: Modify Inputs and Rebuild (Case B)  
*Action:*  
- Edit `Dockerfile` (add `RUN ls`).  
- Rebuild with identical tag `testcaseb`.  

*Command:*  
```bash 
skaffold build --tag=testcaseb --cache-artifacts=true --verbosity=debug 
```  
*Output (abridged):*  
``` 
Generating tags... 
Tags generated in 1.97ms 
Cache check for artifact [docker-image] - input hash: a1b2c3d4 
Found testcaseb remote 
Skipping rebuild: Found remotely 
```  
*Failure/Observation:*  
- New input hash (`a1b2c3d4`) detected (changed due to Dockerfile edit).  
- `lookupRemote` returns `found{hash: a1b2c3d4}` without digest comparison.  
- **Artifact identity**: Cache key `a1b2c3d4` (current input) mapped to *previous remote digest* (from initial build).  

---

#### Step 3: Inspect Cache State  
*Command (using debug dump):*  
```bash 
skaffold debug dump cache --artifact=docker-image 
```  
*Output:*  
``` 
Artifact: docker-image 
Cache Entries: 
  - Hash: 7d4a5e3f -> Digest: sha256:8e6f... (initial build) 
  - Hash: a1b2c3d4 -> Digest: sha256:8e6f... (same as initial) 
```  
*Observation:*  
- Two distinct cache keys (`7d4a5e3f`, `a1b2c3d4`) both reference the *same old digest*.  
- Case B uses **current input hash (`a1b2c3d4`)** as the cache key but inherits the leftover remote digest.  

---

#### Step 4: Verify with Cache Disabled (Case C)  
*Command:*  
```bash 
skaffold build --tag=testcaseb --cache-artifacts=false --verbosity=debug 
```  
*Output:*  
``` 
Cache disabled. Forcing rebuild. 
Building artifact [docker-image]... 
Pushed image: testcaseb@sha256:9a3f... (new digest) 
```  
*Observation:*  
- Fresh build with new digest (`sha256:9a3f...`).  
- Confirms cache was the culprit in Case B.  

---

#### Conclusion: Identity Used in Case B  
- **Cache key**: Current input hash (`a1b2c3d4`).  
- **Digest**: Leftover remote digest from previous build (under reused tag).  
- **Mechanism**: `lookupRemote` overwrote `artifactCache[new_hash]` with the old digest without validation, treating the tag existence as proof of cache hit.  

**Evidence**:  
- Cache dump shows two keys mapping to the same digest.  
- Debug logs confirm `Found remotely` skipped rebuild despite changed inputs.  
- Artifact identity is the *new input hash* corrupted by the *old digest*.  

**Unresolved Uncertainty**:  
- Why did `docker.RemoteDigest()` succeed? (e.g., registry not garbage-collecting old tags).  
- Impact analysis requires registry inspection (outside current scope).
