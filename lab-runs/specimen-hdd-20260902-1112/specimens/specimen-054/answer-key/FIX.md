KNOWN FIX (sealed): python/cpython PR 134231 merge 3fa30d9e9c13c4b84bdc9fc04e33130775679e98.

#128044 updated opcode_metadata_generator.py so unused bytecode numbers identity-deopt to themselves, and also edited the checked-in pycore_opcode_metadata.h. The header patch added numeric rows [119]=119, [120]=120, and [211]=211. Those numbers are already UNPACK_SEQUENCE, YIELD_VALUE, and UNPACK_SEQUENCE_TWO_TUPLE in opcode_ids.h / analysis.opmap, so a real regen-opcode-metadata pass never emits those three numeric keys (named rows already occupy those slots). CI check-generated-files runs make regen-all and sees exactly that three-line deletion.

Repair: commit the regen-all output for Include/internal/pycore_opcode_metadata.h (drop the three colliding identity rows). No generator logic change.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
