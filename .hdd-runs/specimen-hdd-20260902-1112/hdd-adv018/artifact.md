### Field Report: Cache Behavior Investigation

**Summary of initial state:**
- Cache record lists `out.sbom` as an output
- Second build reports `FRESH` cache hit
- `out.sbom` is missing despite cache hit
- Keys match between builds
- Output file creation logic only produces `out.bin`

**Hypothesis:**  
The cache system only validates the input-derived key, not the existence or integrity of declared outputs.

**Experiment 1: Verify cache key sensitivity to outputs**  
*Command:*  
```bash
sed -i "s/outputs = .*/outputs = [\"out.bin\"]  # Modified/" files/cache_dump.py && \
python3 files/cache_dump.py
```

*Output:*  
```
record {"inputs": {"src": "hello"}, "key": "9280cc7e16e9", "outputs": ["out.bin"]}
second FRESH extra_exists False key 9280cc7e16e9
outputs_listed_in_record False
same_key True
```

*Observation:*  
- Key unchanged despite output list modification
- Cache still reports `FRESH` with same key
- Output list alteration doesn't affect cache decision

**Experiment 2: Test output existence requirement**  
*Command:*  
```bash
sed -i $'s/(outdir \/ "out.bin").write_text("bin")/&\n        (outdir \/ "out.sbom").write_text("sbom")  # Added/' files/cache_dump.py && \
python3 files/cache_dump.py
```

*Output:*  
```
record {"inputs": {"src": "hello"}, "key": "9280cc7e16e9", "outputs": ["out.bin", "out.sbom"]}
second FRESH extra_exists True key 9280cc7e16e9
outputs_listed_in_record True
same_key True
```

*Observation:*  
- When both outputs exist, cache reports `FRESH` as expected
- Manual creation of `out.sbom` resolves missing file issue
- Cache still doesn't validate file existence autonomously

**Experiment 3: Verify input sensitivity**  
*Command:*  
```bash
sed -i "s/\"src\": \"hello\"/\"src\": \"changed\"  # Modified/" files/cache_dump.py && \
python3 files/cache_dump.py
```

*Output:*  
```
record {"inputs": {"src": "changed"}, "key": "beef5d26f9c1", "outputs": ["out.bin", "out.sbom"]}
second BUILT extra_exists False key beef5d26f9c1
outputs_listed_in_record True
same_key True
```

*Observation:*  
- Input change generates new key (`beef5d26f9c1` vs original `9280cc7e16e9`)
- Cache miss (`BUILT`) occurs as expected
- Output list remains irrelevant to cache hit decision

**Key Findings:**  
1. Cache freshness depends **exclusively** on input-derived keys  
2. Output declarations (`outputs` list) serve only as metadata  
3. No automatic validation of output existence during cache checks  
4. Cache doesn't detect partial/missing outputs when key matches  
5. System trusts cache entries regardless of filesystem state  

**Conclusion:**  
The listed output names (`out.bin`, `out.sbom`) do **not** participate in freshness decisions. They are merely descriptive metadata attached to the cache record. The cache system validates only the key derived from inputs, creating a disconnect between cache state and actual build artifacts. This explains why `out.sbom` could be missing despite a `FRESH` cache hit.

**Recommendation:**  
Implement post-cache-hit validation checking for existence of all declared outputs before reporting `FRESH`. Current behavior risks broken builds when outputs are manually removed or improperly generated.
