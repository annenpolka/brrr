# Host Red Pen JSON

Write one object (no Markdown fence) matching `hdd-loop` `references/RED_PEN.md`.

Required shape:

```json
{
  "summary": "short diagnosis",
  "preserve_add": [],
  "established_add": [],
  "rejected_add": [],
  "constraints_add": [],
  "open_questions_add": [],
  "harvest_candidates_add": [],
  "affordance_assessment": null,
  "pressure": ["in-world fact or usage task"],
  "redpen_markdown": ""
}
```

`affordance_assessment` may be null on early turns. When set:

```json
{
  "classification": "NOVEL_AFFORDANCE | USEFUL_COMPOSITION | THIN_WRAPPER | NO_SURVIVOR",
  "core_operation": "...",
  "nearest_existing_operation": "...",
  "observable_delta": "...",
  "reason": "..."
}
```

Then choose a coordinator decision in `lab-hdd/lineages/<trial>/DECISION.md` or `lab-hdd/POPULATION.json`:

- CONTINUE_DREAMING
- HARVEST_NOW
- KILL
- PARK_WEIRD
