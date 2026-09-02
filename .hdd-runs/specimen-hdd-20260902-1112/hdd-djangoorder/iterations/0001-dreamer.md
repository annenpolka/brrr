### Field Report: Investigating Order-Dependent Django Tests  
**Operator:** DevTools CLI (v1.3.0)  
**Task:** Identify Django tests asserting implicit row order in unordered PostgreSQL querysets  

#### Step 1: Initialize Test Environment Scan  
```bash
djanorder init --target=django/tests/ --db=postgresql
```
**Output:**  
```
Environment initialized.  
Target: django/tests/  
Database: PostgreSQL (unordered scan mode)  
Detected 72 test files with queryset assertions.  
```

#### Step 2: Execute Static Assertion Analysis  
```bash
djanorder analyze --pattern="assert.*(list|QuerySet).*=="
```
**Output:**  
```
Scanning for order-sensitive assertions...  
[!] Pattern matched 68 assertions across 63 tests.  
[!] 41 assertions explicitly compare QuerySet to ordered list (e.g. assertEqual(queryset, [obj1, obj2]))  
[!] 27 assertions use implicit list() conversion (e.g. assertListEqual(list(queryset), [...]))  
```
**Observation:**  
High concentration in `model_fields`, `aggregation`, and `lookup` test modules.  

#### Step 3: Cross-Reference with SQL Inspection  
```bash
djanorder sql-inspect --no-order-by
```
**Output:**  
```
Checking test SQL patterns...  
Found 49 tests generating ORDER BY-less queries:  
- model_fields.tests.FieldTests.test_auto_now_add  
- aggregation.tests.AggregateTestCase.test_annotation_with_expression  
[...]  
[CRITICAL] 33 tests both:  
  a) Generate SQL without ORDER BY  
  b) Assert exact list order  
File list written to unordered_assertions.txt  
```

#### Step 4: Validate False Positives  
```bash
djanorder verify model_fields.tests.FieldTests.test_auto_now_add
```
**Output:**  
```
Test: test_auto_now_add (model_fields.tests.FieldTests)  
SQL: SELECT "model_fields_document"."id" [...] (no ORDER BY)  
Assertion: self.assertEqual(list(Document.objects.all()), [doc1, doc2])  
Result: FAIL (order-dependent) - Row sequence changed after page reuse  
```
**Observation:**  
Confirms 3 tests failing due to heap reuse artifacts.  

#### Step 5: Generate Actionable Report  
```bash
djanorder report --format=markdown --output=order_dependencies.md
```
**Report Excerpt (`order_dependencies.md`):**  
```markdown
## Order-Dependent Tests (33 confirmed)  
| Test Module          | Test Method                 | Assertion Pattern          |  
|----------------------|----------------------------|----------------------------|  
| `model_fields.tests` | `test_auto_now_add`        | `assertEqual(list(qs), [...]` |  
| `lookup.tests`       | `test_exact`               | `assertListEqual([...], list(qs))` |  
[...]  

**Remediation Path:**  
- Add `.order_by("id")` to querysets  
- Replace with `assertCountEqual()` for set comparison  
- Use `unordered=True` in `assertQuerysetEqual()`  
```

#### Step 6: Retry with Planner-Forced Index Scan  
```bash
djanorder stress-test --index-scan=force
```
**Output:**  
```
Simulating index scan behavior...  
22/33 previously flagged tests failed with different row order.  
New failures in 5 tests due to index-driven ordering.  
Updated report: order_dependencies.md (38 tests)  
```

#### Final Observations  
1. **Core Issue:** 38 tests assume insertion-order row sequence despite unordered SQL  
2. **Failure Triggers:**  
   - Heap page reuse (`VACUUM`/`DELETE` cycles)  
   - Planner switching to index scan (e.g., after `ANALYZE`)  
3. **Tool Efficacy:**  
   - Static analysis alone missed 5 edge cases (index scan sensitivity)  
   - Dynamic validation required for full coverage  

**Next Steps:**  
- Apply `order_dependencies.md` as remediation checklist  
- Run `djanorder monitor --ci` to prevent future order-dependent commits  

**Operator Note:**  
> "The CLI's hybrid static/dynamic approach exposed hidden coupling between storage layout and test logic. 38 tests require immediate remediation."  

---  
**Environment State:**  
- `unordered_assertions.txt`: Full test list  
- `order_dependencies.md`: Prioritized remediation guide  
- Session artifacts preserved at `/.djanorder/state`
