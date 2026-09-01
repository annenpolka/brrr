### Field Report: Exploring CLI Tool `proj` for Code Refactoring  

**Context:**  
Discovered CLI tool `proj` in the environment. Previous commands:  
- `proj --help` → Lists commands: `scan`, `modify`, `chain`, `verify`  
- `proj scan math_utils.py` → Outputs symbols: `[function:calculate, function:helper]`  
- `proj info calculate` → Reveals metadata: `Defined: math_utils.py (line 12), References: 3 (main.py:7, math_utils.py:22, test_math.py:3)`  

**Task:**  
Rename function `calculate` to `compute` in `math_utils.py` and update all references.  

**Procedure:**  
1. **Attempt direct rename:**  
   `proj modify --rename calculate:compute --in math_utils.py`  
   → Error: `Unsupported flag: --rename. Use 'modify --help'`  

2. **Inspect `modify` options:**  
   `proj modify --help`  
   → Output: `Supported: --extract, --inline, --move. No --rename.`  

3. **Test `chain` command:**  
   `proj chain "rename calculate to compute"`  
   → Error: `Invalid chain syntax. Use: chain [command-sequence]`  
   `proj chain "modify --extract calculate as compute"`  
   → Output: `Extracted 'compute' from 'calculate'. Original retained.`  
   → New file: `compute.extracted.tmp` (content: copied function body)  

4. **Manual cleanup attempt:**  
   `proj modify --inline compute --to math_utils.py`  
   → Success: `Inlined 'compute' into math_utils.py (line 27)`  
   → Now *two* functions: `calculate` (line 12) and `compute` (line 27).  

5. **Verify references:**  
   `proj info calculate` → References unchanged (still 3).  
   `proj info compute` → References: `0` (new function not called).  

6. **Attempt reference update:**  
   `proj modify --move calculate:compute --update-refs`  
   → Error: `--update-refs requires --move-destination`  
   `proj modify --move calculate --to math_utils.py:compute --update-refs`  
   → Success: `Moved 'calculate' to 'compute'. Updated 3 references.`  
   → `proj info calculate` → `Symbol not found`  
   → `proj info compute` → References: `3` (updated locations)  

7. **Cleanup temporary artifacts:**  
   `rm *.extracted.tmp` (manual OS command; `proj` lacks cleanup).  

**Observations:**  
- **Workflow:** Renaming requires:  
  1. Extract new symbol (`modify --extract`)  
  2. Move original to new name (`modify --move --update-refs`)  
  3. Manual cleanup of temporary files  
- **Limitations:**  
  - No direct rename command.  
  - `chain` syntax unclear (fails on natural language).  
  - Leaves artifacts (`*.extracted.tmp`).  
- **Success Indicators:**  
  - References updated correctly (verified via `proj info`).  
  - Original function removed after move.  

**Next Steps:**  
- Test multi-file reference updates (e.g., `main.py`).  
- Explore `verify` command for regression checks post-refactor.  
- Report artifact cleanup limitation to tool maintainers.  

**Unresolved Questions:**  
- Can `chain` automate extract→move→cleanup? Syntax documentation missing.  
- Why does `--extract` retain the original? (Design choice for safety?)  

**Conclusion:**  
Achieved rename via `extract`+`move` workflow. Tool functional but verbose for refactors. Artifact management needed.
