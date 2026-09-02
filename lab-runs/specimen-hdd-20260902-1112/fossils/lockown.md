# Fossil: lockown

Date: 2026-09-02
Origin: hdd-gradleid (shared-object wait; Gradle hang / jstack rejected)
Destroyers: DESTROYER_lockown.md (KEEP), DESTROYER_lockown_2.md

**KILL** (Honor, second destroyer). THIN_WRAPPER of caller-labeled
owner/waiter rows. `_label()` is `Thread.name`. CLI has no query input;
stdout is byte-identical to `printf` of `lock L` / `owner holder` /
`waiter blocked` / `held true` (10/10). `run_scene` replica matches 8/8
distinct-name cells. Same-name threads never wait (`_owner != me` is
the label). `snapshot` does not read `threading.Lock`; stickers print
the KEEP pair with the lock unlocked. Timeout un-names the waiter.
First KEEP is not protection. Jstack sticker of a two-thread scene.

Archive left under `lineages/candidate-lockown/`. Do not mutate. Do not
grow attach / jstack / Gradle to escape THIN_WRAPPER. Do not send
Gradle / deadlock theater back to R1. Reimpl of this primitive is not
a survivor.
