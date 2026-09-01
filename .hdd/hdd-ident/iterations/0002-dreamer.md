### Field Report: Operating `same` with Explicit Identity Kinds  

**Command Attempt 1: Testing Omitted Identity Kind**  
```  
$ same file1.txt file1-linked.txt  
Error: Identity kind required. Available kinds:  
  --inode   : Filesystem inode comparison  
  --bytes   : Raw byte content comparison  
  --json    : Canonicalized JSON structure comparison  
Exit code: 2  
```  
*Observation: Confirmed new constraint. Tool now requires explicit identity flags and lists available kinds on omission.*  

**Command Attempt 2: Inode Comparison**  
```  
$ same --inode file1.txt file1-linked.txt  
Result: [IDENTICAL] (inode: 2564)  
```  
```  
$ same --inode file1.txt symlink.txt  
Result: [DISTINCT] (entity types differ: regular file vs symbolic link)  
```  
*Observation: `--inode` strictly compares filesystem nodes. Fails type mismatch even when targets identical.*  

**Command Attempt 3: Byte Content Comparison**  
```  
$ same --bytes file1.txt file1-linked.txt  
Result: [IDENTICAL] (content hash: sha256:a1b2c3)  
```  
```  
$ same --bytes file1.txt symlink.txt  
Result: [IDENTICAL] (content hash: sha256:a1b2c3)  
```  
```  
$ same --bytes file1.txt file2.txt  
Result: [DISTINCT] (content hash mismatch: sha256:a1b2c3 vs sha256:d4e5f6)  
```  
*Observation: `--bytes` ignores metadata/types, comparing only raw content. Symlink resolved to target content.*  

**Command Attempt 4: JSON Comparison**  
Created test files:  
```  
$ echo '{"id":100,"name":"John"}' > record1.json  
$ echo '{"name":"John","id":100}' > record2.json  
$ echo '{"id":100,"name":"Jane"}' > record3.json  
```  
```  
$ same --json record1.json record2.json  
Result: [IDENTICAL] (canonical JSON match)  
```  
```  
$ same --json record1.json record3.json  
Result: [DISTINCT] (value mismatch at /name: "John" vs "Jane")  
```  
```  
$ same --json file1.txt record1.json  
Error: Entity 1 is not valid JSON (line 1, column 1)  
```  
*Observation: `--json` enforces JSON syntax, fails cleanly on non-JSON input. Ignores whitespace/key-order.*  

**Failure Case: Conflicting Identity Kinds**  
```  
$ same --inode --bytes file1.txt file1-linked.txt  
Error: Exclusive identity kinds specified: --inode vs --bytes  
```  
*Adaptation: Retried with single kind:*  
```  
$ same --bytes file1.txt file1-linked.txt  
Result: [IDENTICAL] (content hash: sha256:a1b2c3)  
```  
*Observation: Identity flags are mutually exclusive. Tool rejects ambiguous requests.*  

**Discovered Edge: Empty Files**  
```  
$ touch empty1.txt empty2.txt  
$ same --bytes empty1.txt empty2.txt  
Result: [IDENTICAL] (content hash: sha256:e3b0c44...)  
```  
```  
$ same --inode empty1.txt empty2.txt  
Result: [DISTINCT] (inode: 5120 vs 5121)  
```  
*Observation: Empty files are byte-identical but inode-distinct. Behavior aligns with specified identity kind.*  

**Current Tool Profile**  
- Required: Explicit `--inode`, `--bytes`, or `--json` flag  
- Mutually exclusive identity checks  
- Strict type enforcement (`--inode` fails symlink/file comparison)  
- Content resolution (`--bytes` dereferences symlinks)  
- JSON validation and canonicalization  

**Next Task:** Test directory comparison (previously unexplored).
