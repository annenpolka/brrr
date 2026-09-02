# HDD Ledger

Iteration: 1

## Preserve

- metafile bytesInOutput can stay the 25-byte uniqueKey printer length after outputs.bytes already names the substituted path

## Established

- Packet: Case B bytesInOutput 61 leftover uniqueKey vs bytes 94 substituted; Case D 52 vs 196; Case A never-url tracks source
- publicPath / long asset-names move written CSS but not bytesInOutput on failing_ref

## Rejected

- Invented esbuild / go test transcripts are not host-executed

## Constraints

- Owned labeled uniqueKey-length vs substituted-bytes records. No esbuild.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether bytesInOutput still named leftover uniqueKey length after substitution, omitted like never-url, or a new count because publicPath/filename moved

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover uniqueKey-sized bytesInOutput after the written file already substituted the hashed path
Nearest existing operation: diff metafile inputs.bytesInOutput against outputs.bytes
Observable delta: leftover_uniquekey = bytes_in_output stays uniqueKey-sized while bytes is substituted
Reason: grep of the CSS filename hits both compiles; the miss is uniqueKey length vs substituted url()
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
