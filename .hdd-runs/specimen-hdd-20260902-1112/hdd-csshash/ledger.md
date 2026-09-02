# HDD Ledger

Iteration: 1

## Preserve

- A CSS module [contenthash] can stay the previous identity after a referenced asset's hashed filename has moved

## Established

- Packet: CssUrlDependency has no updateHash; CSS module hash follows CSS source bytes; data.url css-url leftover can shadow assetPath
- Case C: CSS name leftover H_css1, PNG name H_png1, rendered CSS may still contain H_png0

## Rejected

- Invented dep-analyzer / webpack watch transcripts are not host-executed

## Constraints

- Owned labeled identity records. No webpack.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether CSS chunk identity and url() still name the previous PNG [contenthash] after the asset filename moved

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover CSS contenthash and stale css-url after referenced asset identity moved
Nearest existing operation: diff two STATS_JSON asset names and grep url() in the CSS file
Observable delta: leftover_url = url_in_css != png_emitted; leftover_css_hash vs previous compile
Reason: grep of the CSS filename hits both compiles; the miss is url() vs emitted PNG name
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
