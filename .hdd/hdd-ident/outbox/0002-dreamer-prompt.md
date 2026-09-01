# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

An unfamiliar developer CLI is already installed in this environment.

Discover it by using it when two names, paths, or records might or might not refer to the same thing.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

### Field Report: Discovery of Unfamiliar CLI Tool for Entity Identity  

**Command Attempt 1: Invocation Without Arguments**  
Ran `same` to check basic functionality:  
```  
$ same  
Error: Missing required arguments. Usage: same <entity1> <entity2>  
```  
*Observation: Confirmed binary exists. Requires two arguments. Tool name is `same`.*  

**Command Attempt 2: Testing Local File Paths**  
Created test files:  
```  
$ echo "A" > file1.txt  
$ ln file1.txt file1-linked.txt  
$ echo "B" > file2.txt  
```  
Ran comparisons:  
```  
$ same file1.txt file1-linked.txt  
Result: [IDENTICAL] (inode: 2564)  
```  
```  
$ same file1.txt file2.txt  
Result: [DISTINCT] (content hash mismatch)  
```  
*Observation: Tool detects hardlink relationships (inode match) and falls back to content hashing for distinct files.*  

**Command Attempt 3: Testing URIs and Named References**  
```  
$ same https://example.com/resource /mnt/cache/resource-copy  
Result: [IDENTICAL] (ETag: W/"a1b2"; Cache-Status: HIT)  
```  
```  
$ same docker://alpine:latest docker://alpine@sha256:12345abc  
Result: [DISTINCT] (digest mismatch: sha256:789xyz vs sha256:12345abc)  
```  
*Observation: Supports networked resources via URI schemes. Uses ETags/digests for web/docker artifacts.*  

**Command Attempt 4: Ambiguous Record Comparison**  
Input:  
```  
$ same '{"id": 100, "name": "John"}' '{"name": "John", "id": 100}'  
Result: [IDENTICAL] (canonical JSON match)  
```  
```  
$ same 'Employee(101, "Jane")' 'Contractor(101, "Jane")'  
Error: Schema mismatch - class divergence (Employee vs Contractor)  
```  
*Observation: Handles structured data with schema sensitivity. Normalizes JSON but enforces type consistency.*  

**Encountered Limit: Symbolic Links**  
```  
$ ln -s file1.txt symlink.txt  
$ same file1.txt symlink.txt  
Result: [DISTINCT] (target: file1.txt; entity type: symlink vs file)  
```  
*Revised Understanding: Tool distinguishes resource types strictly, even when content-identical. Symbolic links ≠ files.*  

**Failure Case: Unsupported Protocol**  
```  
$ same postgres://user@db/table1 mongodb://localhost/table1  
Error: Unsupported protocol pair (postgres vs mongodb)  
```  
*Adaptation: Retried with schema-extraction flag:*  
```  
$ same --schema postgres://user@db/table1 mongodb://localhost/table1  
Result: [DISTINCT] (schema: column_count=8 vs field_count=12)  
```  
*Observation: Schema comparison requires explicit flag for cross-protocol analysis.*  

**Current Tool Profile**  
- Name: `same`  
- Core capability: Resolves entity equivalence across files/URIs/records  
- Key discriminators: Physical storage (inodes), content hashes, network validators (ETag/digest), schema identity  
- Limitations: No type coercion (symlinks ≠ files), requires `--schema` for cross-protocol record checks  

**Next Task:** Test versioned resource equivalence (`git://repo@v1.2` vs `https://repo/tag/v1.2`).

## Behavior already demonstrated

- The CLI takes two entities and reports identical vs distinct with a stated discriminator.
- Hardlink vs distinct file and JSON key-order canonicalization were attempted locally.
- same A B; symlink treated as distinct type; JSON canonical match; schema mismatch error.


## Newly confirmed limits and corrections

- https ETag, docker digest, postgres vs mongodb schema counts are unsupported.
- No network, docker, or database protocols.
- Identity kind must be explicit (inode, bytes, parsed-json). Do not silently pick a discriminator.
- Operate on real local files.


## New information since the previous report

- There is no network and no container registry. Continue on real local files only.
- The identity kind must be an explicit flag. If omitted, list possible kinds and exit nonzero.
- Do not invent ETags, digests, or schemas.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
