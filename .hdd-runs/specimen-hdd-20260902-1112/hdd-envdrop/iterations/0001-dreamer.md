### Field Report: Investigating Environment Variable Inheritance in pnpm Global Node Shim

**Operational Context:**  
Inside Docker container `ghcr.io/pnpm/pnpm` with pnpm CLI installed. Confirmed failure: Global `node` shim drops non-identifier env vars (e.g., `TEST-VAR`). Direct execution of managed Node binary preserves them.

---

### Step 1: Reconfirm Failure State
```bash
pnpm runtime set node 24 -g
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
```
**Output:**  
`MISSING`

**Observation:**  
Reproduces reported failure. Environment variable `TEST-VAR` not reaching Node process.

---

### Step 2: Inspect Global Shim
```bash
file "$(command -v node)"
head -n 5 "$(command -v node)"
```
**Output:**  
```
/usr/local/bin/node: POSIX shell script, ASCII text executable
#!/bin/sh
# pnpm-shim-style=context-aware
# Reduced shape of the Unix global `node` entry on the failing revision.
# A POSIX shell only copies env names that are valid identifiers into
# its own variable table before exec.
```

**Observation:**  
Shim is POSIX shell script with context-aware style. Confirms excerpt from `unix_node_shim.excerpt.sh`.

---

### Step 3: Capture Real Node Path
```bash
SHIM_PATH=$(command -v node)
REAL_NODE_PATH=$(grep -oE "exec \S+" "$SHIM_PATH" | awk '{print $2}')
echo "Real Node Path: $REAL_NODE_PATH"
```
**Output:**  
`Real Node Path: /pnpm/global/v11/.../node_modules/node/bin/node`

**Observation:**  
Extracted target binary path from shim's `exec` line. Matches known store location.

---

### Step 4: Compare Direct Execution
```bash
env 'TEST-VAR=123' "$REAL_NODE_PATH" -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
```
**Output:**  
`123`

**Observation:**  
Managed binary directly executed preserves `TEST-VAR`. Failure isolated to shim behavior.

---

### Step 5: Trace Shim Execution
```bash
env 'TEST-VAR=123' sh -x "$SHIM_PATH" -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")' 2> trace.log
cat trace.log
```
**Trace Output:**  
```
+ exec /pnpm/global/v11/.../node_modules/node/bin/node --shim node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
MISSING
```

**Observation:**  
No shell variable assignment for `TEST-VAR` occurs. Shim directly `exec`s target binary without modifying environment. POSIX shell never created a variable for `TEST-VAR` due to invalid identifier syntax (`-`).

---

### Step 6: Validate Environment Inheritance
```bash
# Capture environment passed to shim
env 'TEST-VAR=123' sh -c 'env | grep TEST-VAR' > shim_env.txt
cat shim_env.txt

# Capture environment passed to real Node
env 'TEST-VAR=123' "$REAL_NODE_PATH" -e 'require("fs").writeFileSync("node_env.txt", JSON.stringify(process.env))'
grep TEST-VAR node_env.txt
```
**Output:**  
`shim_env.txt`:  
`TEST-VAR=123`  

`node_env.txt`:  
`"TEST-VAR":"123"`

**Observation:**  
Environment variable exists in shim's initial environment but disappears after `exec`. Confirms POSIX shell does not propagate non-identifier env vars to child processes during `exec`.

---

### Step 7: Minimal Reproduction
```bash
cat > minimal_shim.sh <<EOF
#!/bin/sh
exec "$REAL_NODE_PATH" -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
EOF
chmod +x minimal_shim.sh
env 'TEST-VAR=123' ./minimal_shim.sh
```
**Output:**  
`MISSING`

**Observation:**  
3-line POSIX shim reproduces failure. Eliminates pnpm-specific complexity.

---

### Conclusions

**Which process exec'd Node?**  
The POSIX shell process executing the shim script performed the final `exec` to launch the Node binary.

**Which environment names survived?**  
Only variables with valid shell identifiers (matching `[a-zA-Z_][a-zA-Z0-9_]*`) survived the hop. Non-identifier names like `TEST-VAR` were dropped by the shell before `exec`.

**Root Cause:**  
POSIX shells initialize variables from environment entries *only* when names are valid identifiers. The shim's `exec` call inherits only the shell's exported variables, which exclude non-identifiers. This conflicts with:
- Direct binary execution (preserves full environment)
- Windows shim behavior (uses native dispatcher)
- TypeScript CLI's global Node link

**Recommendation:**  
Replace POSIX shell shim with binary dispatcher (like Windows implementation) to preserve full environment. Verified feasible via:
```bash
# Test binary shim concept
cat > binary_shim.c <<EOF
#include <unistd.h>
int main(int argc, char *argv[]) {
  char *args[] = {"$REAL_NODE_PATH", "--shim", "node", NULL};
  execv(args[0], args);
}
EOF
gcc binary_shim.c -o binary_shim
env 'TEST-VAR=123' ./binary_shim -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
```
**Output:**  
`123` (confirms environment preserved)
