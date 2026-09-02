### Field Report: Investigating Encoder Behavior with Developer CLI

**Current Environment State:**  
- Active tool: Unfamiliar developer CLI (installed but unspecified name)  
- Python script `files/two_encoders.py` executed, showing encoder outputs and key presence checks  
- Observed conflict: Downstream interprets missing keys as `true`, but Encoder A omits `false` values  

**Hypothesis:**  
The CLI may provide granular inspection of JSON serialization/deserialization behavior.  

**Action 1: Attempt CLI Discovery**  
*Command:*  
```bash
cli --help
```  
*Output:*  
```
Error: Unrecognized command '--help'.  
Usage: cli <subcommand> [args]  
Subcommands:  
  inspect   Analyze object structures  
  diff      Compare encoded outputs  
  probe     Test encoding/decoding edge cases  
```  
*Observation:*  
CLI responds to `inspect`, `diff`, and `probe` subcommands. No man page or help flags.  

**Action 2: Inspect Encoder A Output**  
*Command:*  
```bash
cli inspect --input '{"name": "x"}' --check-key "flag"
```  
*Output:*  
```
Input: {"name": "x"}  
Key check: "flag"  
→ Key absent: true  
→ Inferred type: null (key missing)  
```  
*Observation:*  
Confirms downstream would interpret missing `flag` as `true`. Matches Python's `"flag" in json.loads(a) == False`.  

**Action 3: Compare Encoder Outputs**  
*Command:*  
```bash
cli diff --left "$(python3 files/two_encoders.py | grep '^A' | cut -d' ' -f2-)" \
         --right "$(python3 files/two_encoders.py | grep '^B' | cut -d' ' -f2-)"
```  
*Output:*  
```
Left (A): {"name":"x"}  
Right (B): {"flag":false,"name":"x"}  

Differences:  
- Left MISSING key: "flag"  
- Right HAS key: "flag" (value: false)  
```  
*Observation:*  
Directly shows Encoder A omits `flag` while Encoder B retains it.  

**Action 4: Test Downstream Behavior**  
*Command:*  
```bash
cli probe --template '{"flag": %s}' --values false null missing
```  
*Output:*  
```
Test case: {"flag": false}  
→ Decoded key present: true (value=false)  

Test case: {"flag": null}  
→ Decoded key present: true (value=null)  

Test case: {}  
→ Decoded key present: false  
  WARNING: Downstream may infer 'true' for missing keys!  
```  
*Observation:*  
CLI explicitly warns about downstream's missing-key behavior. Validates that only Encoder A (output: `{}` for `flag`) triggers this issue.  

**Conclusion from CLI Operations:**  
1. **Encoder A** drops `"flag": false` during serialization → decoded object lacks key.  
2. **Encoder B** retains `"flag": false` → decoded object contains key.  
3. Downstream hazard confirmed: Missing keys (Encoder A) are interpreted as `true`, contradicting original `false` value.  

**Root Cause:**  
Encoder A's `if v is not False` filter removes `false` values during JSON serialization. Downstream's missing-key handling amplifies the mismatch.  

**Recommended Fix:**  
Modify Encoder A to retain `false` values:  
```python
def enc_a(obj):
    return json.dumps(obj)  # Remove value-based filtering
```
