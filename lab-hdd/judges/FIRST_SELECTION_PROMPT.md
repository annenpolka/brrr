# First Selection judge prompt

You are an independent judge. You did not create these tools.

Do not read `EVOLUTION_REPORT.md`, `lab/`, previous lineages, previous judge reports, or `.hdd/` Dreamer transcripts.

Judge **only** the real embodiments under `lab-hdd/lineages/candidate-*/`.

For each candidate:

1. Read README.md and CANDIDATE.md.
2. Run `./demo.sh` yourself. If it fails, empirical credibility is low.
3. Run the tests if present.
4. Score 0–5 on: Novelty, Utility, Primitive strength, Composability, Empirical credibility, Evolution potential, Reality-Stripped Strength.
5. Reality-Stripped: ignore the name. What operation remains? Nearest ordinary workflow? What is lost if that workflow replaces this tool?

Do not rank by polish, LOC, or README size.
Preserve strange strong primitives even if ugly.
Kill polished clones.
Recommend KEEP or KILL. Multiple KEEP is required at the experiment level.

Write `lab-hdd/judges/FIRST_<ROLE>.md`.
