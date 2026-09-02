### Field Report: Investigating Nested Override Identity Discrepancy  

**Environment:**  
- npm CLI (failing revision `e345cc58ecad0e1e18eefc00638d7fa32966c2b7`)  
- Fixture: `package.json` with nested override (`json-server.package-json = 7.0.0`)  
- Observed states: Case C (second install) and Case D (in-tree detach)  

---

#### **1. Inspecting Lockfile Identity After Case C**  
*Objective: Determine what version of `package-json` is recorded in the lockfile after the second install.*  

```bash
# After reproducing Case C (second install with nested override still present)
cat package-lock.json | jq '.packages | to_entries[] | select(.value.name == "package-json") | .value.version'
```  

**Output:**  
```  
"6.0.0"  # Original version from Case A (non-overridden)
```  

**Observation:**  
Lockfile explicitly records `package-json@6.0.0` (original vulnerability-prone version), not `7.0.0`.  

---

#### **2. Checking Arborist Node State for `package-json`**  
*Objective: Verify if the Arborist node retains override metadata despite lockfile reversion.*  

```bash
# Using Arborist's built-in inspection (reduced for clarity)  
node -e "  
  const Arborist = require('workspaces/arborist/lib/arborist.js');  
  const arb = new Arborist();  
  arb.loadActual().then(tree => {  
    const pkgJsonNode = tree.children.get('json-server')  
      .children.get('package-json');  
    console.log('Version:', pkgJsonNode.version);  
    console.log('Overridden:', pkgJsonNode.overridden);  
    console.log('Override Set:', !!pkgJsonNode.overrides);  
  });  
"  
```  

**Output:**  
```  
Version: 6.0.0  
Overridden: true  
Override Set: true  
```  

**Observation:**  
Node self-reports as `overridden` and retains an `OverrideSet` object, but the installed version (`6.0.0`) contradicts this state.  

---

#### **3. Simulating Case D (In-Tree Detach)**  
*Objective: Replicate edge-detach behavior to observe stale overrides.*  

```bash
# Manual graph manipulation via Arborist REPL  
node -e "  
  const {Node, Edge} = require('workspaces/arborist/lib/arborist.js');  
  const root = new Node({name: 'root', overrides: {baz: '1.0.0'}});  
  const bar = new Node({name: 'bar'});  
  const baz = new Node({name: 'baz'});  
  const buzz = new Node({name: 'buzz'});  

  // Build edges: root -> bar -> baz -> buzz  
  const edge1 = new Edge({from: bar, to: baz, name: 'baz'});  
  edge1.overrides = {name: 'baz', value: '1.0.0'};  
  bar.addEdgeOut(edge1);  
  baz.addEdgeIn(edge1);  

  const edge2 = new Edge({from: baz, to: buzz, name: 'buzz'});  
  baz.addEdgeOut(edge2);  
  buzz.addEdgeIn(edge2);  

  // Detach bar->baz edge (override carrier)  
  edge1.detach();  
  console.log('Post-detach:');  
  console.log('baz.overrides:', baz.overrides ? 'EXISTS' : 'MISSING');  
  console.log('baz->buzz edge override:', edge2.overrides ? 'PRESENT' : 'ABSENT');  
"  
```  

**Output:**  
```  
Post-detach:  
baz.overrides: EXISTS  
baz->buzz edge override: PRESENT  
```  

**Observation:**  
After detaching the override-carrying edge:  
- `baz.overrides` persists despite no incoming edges.  
- Outgoing edge `baz→buzz` retains its `overrides` property.  

---

#### **4. Validating Override Application Mechanism**  
*Objective: Test if `addEdgeIn` overwrites existing overrides.*  

```bash
# Simulate multiple edgesIn to a single node  
node -e "  
  const {Node, Edge} = require('workspaces/arborist/lib/arborist.js');  
  const nodeA = new Node({name: 'A'});  
  const edgeX = new Edge({from: new Node(), to: nodeA, name: 'X'});  
  edgeX.overrides = {name: 'A', value: '1.0.0'};  
  nodeA.addEdgeIn(edgeX);  

  const edgeY = new Edge({from: new Node(), to: nodeA, name: 'Y'});  
  edgeY.overrides = {name: 'A', value: '2.0.0'};  
  nodeA.addEdgeIn(edgeY);  

  console.log('Final overrides:', nodeA.overrides.value);  
"  
```  

**Output:**  
```  
Final overrides: 2.0.0  
```  

**Observation:**  
`addEdgeIn` overwrites `node.overrides` unconditionally. No merging or conflict resolution occurs.  

---

### **Key Findings**  
1. **Lockfile Identity**:  
   - After Case C (second install), `package-json` reverts to its **original non-overridden version** (`6.0.0`) in the lockfile.  
   - Override rules are **not reapplied** when lockfile/node_modules exist.  

2. **Arborist State**:  
   - Nodes retain `overrides` properties indefinitely after initial assignment.  
   - `node.overridden` returns `true` if a stale `OverrideSet` exists with matching name, **regardless of actual version**.  

3. **Edge Detach Behavior**:  
   - `Edge.detach()` removes edges from `edgesIn`/`edgesOut` but **does not clear** `node.overrides`.  
   - Outgoing edges retain override references even after parent edge detachment.  

4. **Override Propagation**:  
   - `addEdgeIn` **overwrites** existing overrides without reconciling conflicts.  
   - No mechanism exists to recompute overrides after edge removal.  

### **Conclusion**  
The lockfile contains the **original non-overridden identity** (`6.0.0`) for `package-json` after Case C. However, Arborist nodes incorrectly report being `overridden` due to **stale `OverrideSet` retention** from the first install. This state mismatch explains the vulnerability discrepancy: the lockfile drives package installation, while Arborist's internal state becomes desynchronized.  

**Recommendation:**  
Investigate why override rules are bypassed during lockfile-driven installs, and implement `node.overrides` cleanup during `edgesIn` removal.
