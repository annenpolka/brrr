# OBSERVED

Public python/cpython issue 134236 / PR 134231. Failing world after merge of #128044 (`cc9add695da42defc72e62c5d5389621dac54b2b`, "Mark unknown opcodes as deopting to themselves").

CI job name: `Check if generated files are up to date`.
CI log (issue 134236, actions run 15115778970):

```
Generated files not up to date.
Perhaps you forgot to run make regen-all or build.bat --regen. ;)
```

plus the `_PyOpcode_Deopt` hunk above.

On the failing revision, `generate_deopt_table` in `opcode_metadata_generator.py` does:

1. one named row per `analysis.instructions` (`[inst.name] = deopt`)
2. then, for every `i in range(256)` whose value is **not** in `analysis.opmap.values()`, a numeric row `[i] = i`
3. `assert len(deopts) == 256`

Checked-in `Include/internal/pycore_opcode_metadata.h` on that revision starts `_PyOpcode_Deopt` with numeric keys including 119, 120, and 211.

`Include/opcode_ids.h` on the same revision:

```
#define UNPACK_SEQUENCE                        119
#define YIELD_VALUE                            120
#define UNPACK_SEQUENCE_TWO_TUPLE              211
```

The same generated header also already has named deopt rows later in the table:

```
[UNPACK_SEQUENCE] = UNPACK_SEQUENCE,
[UNPACK_SEQUENCE_TWO_TUPLE] = UNPACK_SEQUENCE,
[YIELD_VALUE] = YIELD_VALUE,
```

`Makefile.pre.in` `regen-opcode-metadata` runs `opcode_metadata_generator.py` against `Python/bytecodes.c` and updates `pycore_opcode_metadata.h`. `regen-all` includes `regen-cases`, which includes `regen-opcode-metadata`.

This packet does not include a local clone; treat the snippets and CI message as the world. Do not execute untrusted checkouts on the host.
