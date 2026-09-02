# FINAL_UNIX — final jury

Judge: Unix
Run: specimen-hdd-20260902-1112
When: 2026-09-02 22:46–23:10 JST
Broad freeze: 22:45. No new Cambrian. Parent `main` `432f954`; no product merge.

Archives scored (KEEP destroyer survivors with host demos this session):

| archive | CLI | last destroyer | tests this session |
|---|---|---|---|
| `lineages/candidate-bind/` | `bindname` sha256 `c7d985ed…` | DESTROYER_20 KEEP | 119/119 OK |
| `lineages/candidate-tagjoin/` | `tagjoin` sha256 `89a5144d…` | DESTROYER_4 KEEP | 52/52 OK |
| `lineages/candidate-emptyunit/` | `emptyunit` sha256 `9e224d35…` | DESTROYER_4 KEEP | 39/39 OK |
| `lineages/candidate-leakorder/` | `leakorder` sha256 `d711f95c…` | DESTROYER_4 KEEP | 24/24 OK |
| `lineages/candidate-ordleak/` | `ordleak` sha256 `4a4bc7d7…` | DESTROYER_4 KEEP | 35/35 OK |

`./demo.sh` exit 0 for all five this session (scratch logs). Honor-KILL fossils (`envlayers`, `reimpl-emptyunit-2`) and leftover-flag TSV THIN_WRAPPERs are not scored as tools.

Unix lens: one object, tiny verbs, text in/out, composition with filters. Not LOC/polish. Disagreement not averaged.

---

## bindname

**Object.** For one import, the body that would run vs other same-name defs this import did not bind. Leftover `ast.py` is the leftover helper, not Homebrew `ast.parse`.

`grep def parse` hits both. Isolated `spec_from_file_location` + `inspect.getsource` names one object you already loaded. bindname joins them: leftover body, `also` the moved def, `same_function False`, leftover stdlib isolate (path-shadowable helper vs frozen/builtin refuse). Mutate-16 const-env (BoolOp operand, mixed assign, `_ATTR_MISSING` through collections, MatchSequence) is still the same object. Nested-class / FunctionDef sentinel / Name-bases / exec `__init__` / While stay parked (do not exec).

This is the Unix verb in the batch.

| axis | score | note |
| --- | ---: | --- |
| Novelty | 4 | Missing locator, not a new cosmology. |
| Utility | 4 | I would run this tomorrow on a stale `from util import parse`. |
| Primitive strength | 4 | One object. Const-env growth did not add a second product. |
| Composability | 3 | TSV; `-C DIR`. Not a stdin filter. |
| Empirical credibility | 5 | 119/119; leftover `ast.py` host-probed through DESTROYER_20. |
| Evolution potential | 3 | Parks need an interpreter. Stop. |
| Reality-Stripped Strength | 4 | Pairing + leftover isolate. |
| Cross-specimen transfer | 3 | Specimen-013 owned; leftover isolate is the transfer. |

**Decision: KEEP. PATH install.**

---

## tagjoin

**Object.** A json field that is a list-map key *and* optional (omitempty), often on the element type.

Two greps (`omitempty`, `listMapKey`) hit. The join is the object. Four KEEP destroyers did not find leftover-identity that AST-static can cut without becoming a kube codegen.

| axis | score |
| --- | ---: |
| Novelty | 3 |
| Utility | 3 |
| Primitive strength | 3 |
| Composability | 3 |
| Empirical credibility | 4 |
| Evolution potential | 2 |
| Reality-Stripped Strength | 3 |
| Cross-specimen transfer | 3 |

**Decision: KEEP in the drawer. Not a PATH install.** I already have `grep`. The join is real; I will not add a binary for CRD authors only.

---

## emptyunit

**Object.** Completed-only units that requeue into `send_runtest_some` of an empty index list: hang if assigned send is `()`.

pytest-xdist specific. Four KEEP. Do not grow a LoadScopeScheduling.

| axis | score |
| --- | ---: |
| Novelty | 3 |
| Utility | 3 (pytest maintainers) |
| Primitive strength | 3 |
| Composability | 2 |
| Empirical credibility | 4 |
| Evolution potential | 2 |
| Reality-Stripped Strength | 3 |
| Cross-specimen transfer | 2 |

**Decision: KEEP lineage. Not PATH.** Remember the hang. Do not install a pytest-xdist satellite.

---

## leakorder / ordleak

**Object.** Two-order run: what leaked when only order changed; the sufficient exposing order.

Competing implementations of one object. Bakeoff exists. Isolation (helper-module, class attrs) is the mutate that made them KEEP.

| axis | leakorder | ordleak |
| --- | ---: | ---: |
| Novelty | 3 | 3 |
| Utility | 3 | 3 |
| Primitive strength | 3 | 3 |
| Composability | 3 | 3 |
| Empirical credibility | 4 | 4 |
| Evolution potential | 2 | 2 |
| Reality-Stripped Strength | 3 | 3 |
| Cross-specimen transfer | 3 | 3 |

**Decision: KEEP the family as one drawer object. Not PATH.** Prefer `ordleak` if I had to pick one (isolation). Do not install both.

---

## Tomorrow (Unix)

Install: **bindname**.

Remember without PATH: tagjoin join, emptyunit hang, order-leak family.

Empty slots: yes.
