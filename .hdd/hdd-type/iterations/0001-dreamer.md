### Field Report: Exploring the Unfamiliar CLI Tool  

**Situation**: Encountered a type mismatch in a TypeScript codebase between an API response interface (`UserData`) and a frontend component's expected props (`UserProfileProps`).  

**Actions Taken**:  
1. Ran `mismatch scan ./src` to detect contract violations.  
   ```plaintext
   [OUTPUT]  
   Detected 1 contract mismatch:  
   - File: ./src/components/UserProfile.tsx  
     Line 23: Component 'UserProfile' expects 'age: number'  
   - File: ./src/api/userService.ts  
     Line 8: Endpoint 'fetchUser' returns 'age: string'  
   ```  

2. Attempted auto-resolution with `mismatch fix --strategy=coerce ./src/api/userService.ts`:  
   ```plaintext
   [ERROR]  
   Auto-fix failed:  
   Ambiguous conversion path (string→number).  
   Requires manual input.  
   ```  

3. Investigated conversion options using `mismatch explain ./src/api/userService.ts:8.age`:  
   ```plaintext
   [OUTPUT]  
   Property 'age': string → number  
   Available transforms:  
   1. Number(age)        // Coercion (risky for non-numeric strings)  
   2. parseInt(age, 10)  // Safe integer conversion  
   3. Custom mapper       │ Run `mismatch generate-mapper`  
   ```  

4. Generated a custom mapper stub:  
   ```bash
   mismatch generate-mapper --name=ageConverter --input=string --output=number
   ```
   ```typescript
   [GENERATED FILE: ./mappers/ageConverter.ts]  
   export default function ageConverter(input: string): number {  
     // IMPLEMENT: Add conversion logic  
     throw new Error('Not implemented');  
   }  
   ```  

5. Linked the mapper to the mismatch:  
   ```bash
   mismatch attach-mapper ./src/api/userService.ts:8.age --mapper=./mappers/ageConverter.ts
   ```  
   ```plaintext
   [SUCCESS]  
   Applied mapper to:  
   - api/userService.ts:8.age  
   - components/UserProfile.tsx:23.age (inferred)  
   ```  

6. Re-ran validation:  
   ```bash
   mismatch verify --changed
   ```  
   ```plaintext
   [OUTPUT]  
   Contract restored:  
   - All type flows consistent via 'ageConverter'  
   ```  

**Key Observations**:  
- The tool:  
  - Identifies bidirectional contract mismatches (API↔UI)  
  - Generates stubs for custom transformations  
  - Maintains traceability between mismatched points  
- **Limitations**:  
  - Avoids speculative type conversions (requires explicit mapper)  
  - No automatic code modification for ambiguous cases  
  - Mapper files must be manually implemented  

**Next Steps**:  
- Test runtime behavior after implementing `ageConverter` logic  
- Verify propagation to other usage points with `mismatch trace ./mappers/ageConverter.ts`  

---  
**Environment State**:  
- Active mapper binding between `userService.ts` and `UserProfile.tsx`  
- Custom mapper stub requires implementation  
- Tool now monitors `age` type flows project-wide
