# Throughput

Vacant inference slots take the next ready job. Clock milestones are deadlines.
R1/test waits register a handle and free the slot. No isomorphic-Dream filler.

Updated: 2026-09-09 17:44:04 JST

Jobs recorded: 14
Intentional idle gaps >120s: 0

| When JST | Job | Status | Slot | Note |
| --- | --- | --- | --- | --- |
| 2026-09-09 17:30:06 JST | bootstrap | completed | coordinator | init+export+preview-dream; no Dream yet; 1130/9/2 not re-inited |
| 2026-09-09 17:33:22 JST | dream-0001 | started | r1-1 | live deepseek/deepseek-r1 via dream.sh; HTTP success will not be recorded as tool success |
| 2026-09-09 17:33:22 JST | host-verify-case-001-deno | completed | worker-1 | 実機 two-invocation deno run on public files; not passed to Dreamer |
| 2026-09-09 17:35:01 JST | collect-pilot-expand-resume | started | worker-2 | resume existing collection a9328ef4 200req/600s isolated expand root; Dreamer not waiting |
| 2026-09-09 17:35:21 JST | collect-pilot-expand-resume | started | worker-2 | resume existing collection a9328ef4 200req/600s; Dreamer not waiting |
| 2026-09-09 17:37:40 JST | collect-pilot-expand-resume-200 | started | worker-2 | resume a9328ef4 200req/600s after short probe; not Dreamer-facing |
| 2026-09-09 17:39:00 JST | host-verify-14011 | completed | worker-1 | pytest 9.0.1 on public snippet; HOLD; not Dreamer |
| 2026-09-09 17:39:00 JST | host-verify-14591 | completed | worker-1 | pytest 9.0.3 vs 9.1.0 on public snippet; HOLD; not Dreamer |
| 2026-09-09 17:39:54 JST | host-verify-13479 | completed | worker-1 | pytest 8.4.1 + freezegun on public snippet; HOLD; not Dreamer |
| 2026-09-09 17:40:32 JST | host-verify-13885 | completed | worker-1 | pytest 8.4.1/9.0.1 on skipIf+autouse snippet; HOLD; not Dreamer |
| 2026-09-09 17:42:09 JST | dream-0001 | completed | r1-1 | http-ok tool_success=false; host Red Pen recorded |
| 2026-09-09 17:42:09 JST | redpen-0001 | completed | coordinator | host Red Pen; HTTP not treated as tool success |
| 2026-09-09 17:42:37 JST | dream-0002 | started | r1-1 | second live R1 after host Red Pen; HTTP will not be tool success |
| 2026-09-09 17:44:04 JST | collect-pilot-expand-resume-200 | completed | worker-2 | 200 requests, INVOCATION_REQUEST_LIMIT, unfinished remain; HOLD screens not flipped to PASS |
