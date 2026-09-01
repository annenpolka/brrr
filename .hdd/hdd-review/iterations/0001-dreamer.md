### Field Report: Exploring the Unfamiliar Developer CLI

**Initial State**:  
Working in a directory containing a modified Python file `src/api.py` with unshared changes. No prior knowledge of the CLI's syntax.

**Attempt 1**: Ran base command to observe behavior:  
```bash
$ dev
```
**Output**:  
```
ERROR: No target specified.  
Available targets:  
  - review [path]  
  - verify [path]  
  - snapshot [id]  
Use 'dev --explain' for command details.
```

**Observation**:  
The CLI rejects bare commands and requires explicit subcommands. "Review" seems relevant to our task.

**Attempt 2**: Tried help flag on review subcommand:  
```bash
$ dev review --help
```
**Output**:  
```
review [path]: Analyzes local diffs  
Flags:  
  --annotate   : Enable inline comment mode  
  --strict     : Enable linting checks (default: off)  
Error: Path required when not in .devctx scope.
```

**Observation**:  
1. Requires explicit file/directory path  
2. References unknown ".devctx scope" – possibly a project context system  
3. "annotate" flag suggests interactive review capability  

**Attempt 3**: Ran review against modified file:  
```bash
$ dev review src/api.py --annotate
```
**Output**:  
```diff
Reviewing: src/api.py
[Loaded .devctx (v2) from /projects/api/.devctx]
▼ Modified function: fetch_data (line 18)  
───────────────────────────────────────────
-    response = requests.get(url, timeout=5)  
+    response = requests.get(url, timeout=10)  
───────────────────────────────────────────
[ANNOTATION MODE]  
Type comment or:  
  (n)ext  (p)revious  (a)dd note  (q)uit
```

**Observation**:  
1. Auto-detected project context (.devctx)  
2. Shows focused diff with navigation controls  
3. Changed behavior: CLI enters interactive mode despite no terminal prompt in output  

**Attempt 4**: Tested annotation feature:  
```bash
a Why increase timeout? Consider configurable value instead.
```
**Output**:  
```
Annotation recorded at [fetch_data].  
Use 'dev snapshot save' to persist notes.
```

**Attempt 5**: Tried navigating to next change:  
```bash
n
```
**Output**:  
```
▼ Added function: validate_response (line 41)  
++++++++++++++++++++++++++++++++++++++++++++
+ def validate_response(res):  
+     if res.status_code != 200:  
+         raise CustomError("API failure")  
++++++++++++++++++++++++++++++++++++++++++++
```

**Observation**:  
Navigation works within the file. No other changes detected.

**Attempt 6**: Verified change integrity:  
```bash
$ dev verify src/api.py
```
**Output**:  
```
Verifying src/api.py...  
[!] Potential issue: validate_response raises bare CustomError  
  Recommendation: Add error logging or return codes  
[✓] Timeout change passes basic checks  
Result: 1 advisory, 0 critical
```

**Key Discoveries**:  
1. **Context-driven**: Requires either explicit paths or pre-configured `.devctx`  
2. **Workflow**:  
   - `review` → Interactive change inspection  
   - `verify` → Automated quality checks  
   - `snapshot` → Annotation persistence (untested)  
3. **Strict Mode**: Disabled by default – enables deeper validation per `--help`  
4. **Output Behavior**: Diff presentation prioritizes semantic chunks over line numbers  

**Unresolved Questions**:  
- How `.devctx` gets created/modified?  
- Snapshot system interaction model  
- Sharing mechanism (implied by "before shared" context but no observed command)  

**Next Steps**:  
1. Test `dev snapshot list` for saved annotations  
2. Explore if `dev share` exists (not listed but implied by task context)  
3. Experiment with `--strict` flag during verification  

**Session State**:  
Annotations remain ephemeral until snapshot creation. Verified issues require manual resolution.
