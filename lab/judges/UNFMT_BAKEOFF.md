# Inverse-printf bakeoff (empirical)

Source: critic `01a01ae6-5b17-7e80-ad5f-bcd84fc76620` ~01:50 JST. Same pastes, four binaries.

## Battery

5/5 = kizu hit + sitbone camera + 7-hole Logger + tenaoshi untracked + correct miss.

| Tool | Battery | Notes |
| --- | --- | --- |
| invert | 5/5 | Named holes, cleanest kizu rank, stream-shaped. **Lineage vehicle.** |
| unfmt-13 | 5/5 | Named holes; slowest walker; noisier kizu rank. |
| stencil | 5/5 | Honest unfmt-08 reimpl; camera fixed; still anonymous; leaks `git {} failed`. Walker spare. |
| unfmt-08 | 4/5 | Camera miss (nested Swift quotes). Cleanest *walker* rank on kizu. |

## Decision

Carry **invert**. Keep stencil as walker spare. Do not keep two walkers. If one-shot `-C repo` is needed, wrap invert’s kernel in an optional producer (`rg` / `git ls-files`), do not grow a second ignore policy.

WAVE3 “stencil beats original on camera” is confirmed. Invert still needs a stream; it is not a better one-shot walker.
