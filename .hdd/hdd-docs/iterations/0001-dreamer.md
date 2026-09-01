### Field Report: Exploring the Unfamiliar CLI  
**Operational Log**  

**1. Initial Probe**  
Ran base command without arguments to trigger system response:  
```bash
$ devcli
```  
**Observation**:  
```  
Error: Missing subcommand.  
Available: init, build, run, inspect, config  
Use 'devcli <command> --help' for details  
```  

**2. Testing `init` Workflow**  
Attempted project initialization with minimal arguments:  
```bash  
$ devcli init --type web ./project_dir  
```  
**Observation**:  
```  
Project scaffold failed:  
[ERR] Directory './project_dir' exists but lacks .manifest file  
HINT: Run 'devcli init --force' to overwrite or 'devcli inspect dir' to diagnose  
```  
**Action**: Used `inspect` to investigate directory state:  
```bash  
$ devcli inspect dir ./project_dir  
```  
**Output**:  
```  
Directory status:  
  - Contains: 3 .js files, 2 .md files  
  - Missing: .manifest (required)  
  - Detected: legacy config (v0.8) in package.json  
```  

**3. Forced Initialization**  
Applied `--force` flag based on error hint:  
```bash  
$ devcli init --type web --force ./project_dir  
```  
**Observation**:  
```  
Overwriting directory...  
WARNING: Converted package.json → .manifest (v2.3)  
Success: Project initialized. Run 'devcli build' next  
```  

**4. Build Process Test**  
Executed build command:  
```bash  
$ devcli build  
```  
**Output**:  
```  
Building target: web-default  
[STAGE] Dependency resolution... OK  
[STAGE] Transpilation... FAILED  
Error: Missing runtime profile (required for JSX)  
HINT: Set via 'devcli config runtime.profile=env'  
```  

**5. Configuration Adjustment**  
Attempted to set required runtime profile:  
```bash  
$ devcli config set runtime.profile env  
```  
**Observation**:  
```  
Config update failed:  
'env' is not a valid profile. Choices: node, browser, hybrid  
```  
**Retry**:  
```bash  
$ devcli config set runtime.profile browser  
```  
**Output**:  
```  
Configuration updated: runtime.profile = browser  
```  

**6. Build Retry**  
Re-ran build with updated config:  
```bash  
$ devcli build  
```  
**Observation**:  
```  
Building target: web-default  
[STAGE] Dependency resolution... OK  
[STAGE] Transpilation... OK  
[STAGE] Optimization...  
Error: Asset pipeline requires 'devcli build --with-assets'  
```  

**7. Asset Handling Discovery**  
Executed suggested flag:  
```bash  
$ devcli build --with-assets  
```  
**Output**:  
```  
Building target: web-assets  
[ASSET] Processed 12 images → /dist/media  
Success: Built to /dist (size: 14.7MB)  
```  

**8. Runtime Execution Test**  
Launched project:  
```bash  
$ devcli run  
```  
**Observation**:  
```  
Runtime error:  
Port 8080 occupied by process 28491  
HINT: Use 'devcli run --port-auto' or kill conflicting process  
```  
**Action**: Used port auto-selection:  
```bash  
$ devcli run --port-auto  
```  
**Output**:  
```  
Running web server (profile: browser)  
• API: http://localhost:6093  
• Assets: http://localhost:6093/media  
[Ctrl+C to exit]  
```  

**Key Findings**  
- **Stateful Configuration**: Settings persist between commands (`runtime.profile` affected build)  
- **Contextual Errors**: Hints adapt to environment state (port conflicts, directory contents)  
- **Asset Separation**: Non-trivial workflow requiring explicit asset flag  
- **Legacy Conversion**: Automatic v0.8 → v2.3 manifest migration during forced init  
- **Strict Validation**: Rejects invalid config values with enumerated options  

**Unresolved Questions**  
- How project type (web) affects build output?  
- Purpose of `.manifest` vs traditional package managers?  
- Can runtime profile be set per project rather than globally?  

**Next Steps**  
- Test `inspect` on build artifacts  
- Attempt multi-target build (if supported)  
- Profile resource usage during runtime
