# Throughput

Vacant inference slots take the next ready job. Clock milestones are deadlines.
R1/test waits register a handle and free the slot. No isomorphic-Dream filler.

Updated: 2026-09-09 17:55:25 JST

Jobs recorded: 30
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
| 2026-09-09 17:45:36 JST | collect-pilot-expand-resume-200b | started | worker-2 | second 200-req resume slice; Dreamer not waiting |
| 2026-09-09 17:48:24 JST | dream-0002 | completed | r1-1 | http-ok tool_success=false; invented tool CLI; host Red Pen recorded |
| 2026-09-09 17:48:24 JST | redpen-0002 | completed | coordinator | host Red Pen; HTTP not treated as tool success |
| 2026-09-09 17:48:37 JST | dream-0003 | started | r1-1 | third live R1 after Red Pen 0002; HTTP will not be tool success |
| 2026-09-09 17:48:37 JST | collect-other-1730 | started | worker-3 | isolated root .brrr-corpus/pilot-1730-other github-other-ecosystems-v1 200/600; expand root still busy |
| 2026-09-09 17:49:42 JST | collect-pilot-expand-resume-200b | completed | worker-2 | 200 requests INVOCATION_REQUEST_LIMIT EXIT:3; expand coordinator free |
| 2026-09-09 17:49:42 JST | collect-pilot-expand-resume-200c | started | worker-2 | resume a9328ef4 after busy coordinator exited; 200/600 |
| 2026-09-09 17:50:45 JST | host-verify-index | completed | worker-1 | index of HOLD 実機; not Dreamer-facing; no PASS minted |
| 2026-09-09 17:53:10 JST | collect-expand-resume-200c | completed | worker-2 | EXIT:3 RATE_WAIT; uv issues now complete_for_policy |
| 2026-09-09 17:53:10 JST | collect-other-1730 | completed | worker-3 | EXIT:3 INVOCATION_REQUEST_LIMIT 16 cargo complete; pending 25 |
| 2026-09-09 17:53:10 JST | collect-other-1730-resume | started | worker-3 | resume 1c7ed67b 200/600 isolated 1730-other root |
| 2026-09-09 17:54:16 JST | dream-0003 | completed | r1-1 | http-ok tool_success=false; invented javix; THIN_WRAPPER; stop isomorphic Dreams |
| 2026-09-09 17:54:16 JST | redpen-0003 | completed | coordinator | host Red Pen THIN_WRAPPER; no further isomorphic R1 on this trial |
| 2026-09-09 17:54:49 JST | uv-review | completed | worker-1 | 9 uv issues HOLD; no PASS; not Dreamer |
| 2026-09-09 17:54:49 JST | first-selection | completed | coordinator | KEEP 0; KILL fictional CLIs; HOLD extras; FIRST_SELECTION does not disable contamination |
| 2026-09-09 17:54:49 JST | collect-expand-resume-200d | started | worker-2 | resume a9328ef4 after RATE_WAIT passed; 200/600; not isomorphic Dream filler |
