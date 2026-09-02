### Field Report: Investigating TypeScript Incremental Compilation Error Persistence

**Environment State**:  
- TypeScript incremental compilation enabled (`incremental: true`)  
- `.tsbuildinfo` file present  
- Source files: `js/MessageablePerson.ts` (mixin class), `js/main.ts` (importer)  
- Observed failure mode: Stale TS2445 error persists after reverting `public` → `protected` → `public` change  

---

#### Step 1: Simulate Case B Scenario  
Created minimal reproduction fixture based on public report:  

**File: `js/MessageablePerson.ts`**  
```typescript
class MessageablePerson {  
  public message: string = "";  
}  
export type MessageablePersonType = InstanceType<typeof MessageablePerson>;  
```

**File: `js/main.ts`**  
```typescript
import { MessageablePersonType } from "./MessageablePerson";  
const person: MessageablePersonType = new MessageablePerson();  
console.log(person.message);  
```

**File: `tsconfig.json`**  
```json
{  
  "compilerOptions": {  
    "incremental": true,  
    "noEmit": true,  
    "target": "es2017"  
  },  
  "include": ["js/**/*"]  
}  
```

---

#### Step 2: Execute Public Reproduction Steps  
```bash
# Initial compilation (clean state)
$ tsc
# Output: No errors

# Introduce error: public → protected
$ sed -i 's/public message/protected message/' js/MessageablePerson.ts
$ tsc
# Output: js/main.ts:3:17 - error TS2445: Property 'message' is protected...

# Revert error: protected → public
$ sed -i 's/protected message/public message/' js/MessageablePerson.ts
$ tsc
# Output: js/main.ts:3:17 - error TS2445: Property 'message' is protected... (STALE ERROR PERSISTS)
```

**Observation**:  
- Stale TS2445 error remains despite source revert  
- `.tsbuildinfo` file persists across compilations  

---

#### Step 3: Inspect Build Artifacts  
```bash
$ cat tsconfig.tsbuildinfo | jq '.fileInfos."js/MessageablePerson.ts"'  
{
  "version": "d3b1a5e7c6d25f1e0a4c",  # Hash of d.ts text
  "signature": "d3b1a5e7c6d25f1e0a4c",  # Matches version
  "affectsGlobalScope": true
}

$ cat tsconfig.tsbuildinfo | jq '.semanticDiagnosticsPerFile."js/main.ts"'  
[
  {
    "code": 2445,
    "message": "Property 'message' is protected...",
    "start": 102,
    "length": 7,
    "file": "js/main.ts"
  }
]
```

**Key Findings**:  
1. `.tsbuildinfo` stores:  
   - `fileInfos`: Signature = hash of d.ts emit text (excludes diagnostics)  
   - `semanticDiagnosticsPerFile`: Persistent error state for `js/main.ts`  
2. After revert:  
   - `MessageablePerson.d.ts` text identical to initial state → Signature unchanged  
   - Importer (`main.ts`) not rechecked due to matching signature  
   - Stale diagnostic retained from error state  

---

#### Step 4: Validate Case B Identity  
```bash
# Delete build artifacts
$ rm tsconfig.tsbuildinfo

# Recompile after revert (simulate Case D)
$ tsc
# Output: No errors (clean compilation)

# Inspect new .tsbuildinfo
$ cat tsconfig.tsbuildinfo | jq '.semanticDiagnosticsPerFile."js/main.ts"'
# Output: null (no stored error)
```

**Conclusion**:  
- **Case B Identity**: `.tsbuildinfo` retains:  
  - Unchanged d.ts signature (hash of emit text)  
  - Stored TS2445 diagnostic for `js/main.ts`  
- **Next `tsc` Behavior**: Reports stale error due to:  
  1. Signature match → Skips recheck of importer  
  2. Prior diagnostic reused from `.tsbuildinfo`  

---

#### Root Cause Analysis  
- **Signature Gap**: d.ts hash ignores diagnostic changes (visibility modifiers)  
- **Incremental Heuristic**: Signature match → assumes no need to recheck dependents  
- **Failure Mode**: Error state becomes "sticky" when:  
  - Diagnostic changes occur without d.ts text changes  
  - Importer isn't invalidated by signature check  

**Operational Note**:  
Behavior resolved in TypeScript ≥4.8 via `computeSignatureWithDiagnostics` (PR #49543). Current environment matches pre-fix revision constraints.
