# FIX (sealed)

pytest-dev/pytest-rerunfailures PR 340 / issue 268.

Merge commit: 6df6fb59dc92bb940b240200820474ddfa3064e3
Head commit: e3e64ad5339992ace54d0b858724f76f934ce698
Title: Create a fresh test class instance for each rerun

pytest caches one class instance per test item. The rerun loop reuses the same item, so attributes written onto `self` survived into the next attempt. pytest 6 reconstructed instances more often; pytest 7 made the reuse visible.

Repair: add `_discard_test_class_instance(item)` to the existing pre-rerun cleanup. It drops the item's cached class instance and the method bound to that instance so pytest lazily constructs both again. Cached results of fixtures whose scope is class or higher stay in place.

Do not expose this file to Dreamers, initial Red Pen, or initial Grounders.
