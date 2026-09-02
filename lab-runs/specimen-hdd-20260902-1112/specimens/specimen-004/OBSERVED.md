# OBSERVED

Public npm/cli#9876 / PR 9877. Empty cache, `npm install vite`:

| | before (failing) | after (fixed, not shown to you as a solution) |
| registry requests | 86 | 54 |
| cached registry data | ~121MB | ~72MB |

Final install: ~10 packages. Fetches include full packuments for optional peers that are not installed.

The failing world still produces a valid tree; the cost and the fetch set are the surprise.
