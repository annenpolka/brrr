# Host 実機 for stored issue 14971 (not a public HDD bundle)

Not Dreamer-facing. Not quality PASS. Not 未知holdout. Not merged onto coordinator main.

Reconstructed the five quoted files from the stored issue body. Did not include the reporter's causal trace in any consumer seed.

## pytest versions on this host (Python 3.14 venvs in this directory)

| Command | 9.1.1 | 8.4.2 |
| --- | --- | --- |
| `python -m pytest tests/services/test_a.py tests/test_top.py tests/services/test_b.py -q -p no:cacheprovider` | `..E` then `fixture 'nested_fixture' not found` for `test_b` | `...` 3 passed |

Matches the reported 9.1.1 error / 8.4.2 pass on this reconstruction. OS/Python are not the reported 3.10.19.

## runpair around the 9.1.1 command

`first.rc=1` `second.rc=1` `added=[]` both times. No cwd sidecar appears. runpair's observable delta is empty here; this case is not a KEEP transfer for runpair.

## Corpus

No View, no leakage PASS, no export. HOLD until a byte-range View exists that omits the internal-trace paragraph.
