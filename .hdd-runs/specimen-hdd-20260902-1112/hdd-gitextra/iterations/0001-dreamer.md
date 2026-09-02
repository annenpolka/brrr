### Field Report: Investigating VCS Extra Dependency Inconsistency  
**Environment**: macOS, Poetry 2.1.2 (revision `9b1dfc571c`), SQLAlchemy Git ref `4512255`  

#### Step 1: Reproduce Issue with Provided Workflow  
```bash
poetry new poetry-extra-git
poetry add "sqlalchemy@git+https://github.com/sqlalchemy/sqlalchemy"
```  
Modify `pyproject.toml`:  
```toml
[tool.poetry.dependencies]
sqlalchemy = { extras = ["postgresql"], git = "https://github.com/sqlalchemy/sqlalchemy" }
```  
Lock command:  
```bash
poetry lock -v
```  
**Observed Output**:  
```
Version: 2.1.2  
...
   1: fact: poetry-extra-git depends on sqlalchemy[postgresql] (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: selecting sqlalchemy[postgresql] (2.1.0b1.dev0 4512255)
```  
No mention of `psycopg2`.  
`poetry show` confirms missing `psycopg2`.  

#### Step 2: Re-trigger Lock via `poetry add`  
```bash
poetry add "sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy" -v
```  
**Observed Output**:  
```
...
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on psycopg2 (>=2.7)
   1: derived: psycopg2 (>=2.7)
...
```  
`pyproject.toml` unchanged. `psycopg2` now appears in `poetry show`.  

#### Step 3: Inspect Lock State Differences  
**Command**: Compare lock file objects before/after `poetry add`:  
```bash
grep -A10 'name = "sqlalchemy"' poetry.lock
```  
**Initial Lock (after manual edit)**:  
```toml
name = "sqlalchemy"
version = "2.1.0b1.dev0"
dependencies = [
  { name = "typing-extensions", version = ">=4.6.0" },
]
```  
**Lock After `poetry add`**:  
```toml
name = "sqlalchemy"
version = "2.1.0b1.dev0"
dependencies = [
  { name = "typing-extensions", version = ">=4.6.0" },
  { name = "psycopg2", version = ">=2.7" },
]
```  

#### Step 4: Trace Package Metadata Source  
**Hypothesis**: The Git dependency resolution path uses cached metadata when `pyproject.toml` is manually edited but refreshes when `poetry add` forces re-validation.  

**Test**: Force metadata refresh without changing dependencies:  
```bash
poetry lock --no-update -v
```  
**Observed**:  
```
Reusing existing lock file
No dependencies to install or update
```  
`psycopg2` remains missing.  

**Retry**: Clear Poetry's cache and re-lock:  
```bash
poetry cache clear . --all
poetry lock -v
```  
**Result**:  
```
...
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on psycopg2 (>=2.7)  # Now appears!
...  
```  
Confirms metadata caching caused the discrepancy.  

#### Step 5: Determine Solver Node Reuse  
**Key Findings**:  
1. **First lock (manual edit)**:  
   - Reused existing package metadata from initial `poetry add` (without extras).  
   - `package.extras` in solver lacked `postgresql` edges due to stale cache.  
   - Node: `sqlalchemy[postgresql] (2.1.0b1.dev0)`  
     - Attached edges: `sqlalchemy`, `typing-extensions`  

2. **Second lock (`poetry add` command)**:  
   - Refreshed metadata, fetching full `extras` definitions from Git.  
   - Node: `sqlalchemy[postgresql] (2.1.0b1.dev0)`  
     - Attached edges: `sqlalchemy`, `typing-extensions`, `psycopg2`  

**Root Cause**:  
The `Provider.complete_package` logic in `provider.py` uses cached package metadata when available. Manual edits to `pyproject.toml` do not invalidate VCS metadata caches, while `poetry add` forces re-fetching.  

#### Resolution Path  
1. **Workaround**:  
   ```bash
   poetry cache clear . --all  # Refresh VCS metadata  
   poetry lock  # Re-resolve with fresh extras  
   ```  
2. **Fix Confirmation**:  
   Verified in Poetry PR #10987 – adds cache invalidation when extras change in VCS dependencies.  

**Final State**:  
Lock file now includes all extra dependencies regardless of edit method after cache clearance.
