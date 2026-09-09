# Throughput

Vacant inference slots take the next ready job. Clock milestones are deadlines.
R1/test waits register a handle and free the slot. No isomorphic-Dream filler.

Updated: 2026-09-09 18:10:07 JST

Jobs recorded: 63
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
| 2026-09-09 17:56:44 JST | other-eco-review | completed | worker-3 | 6 cargo issues HOLD; NO_RUNNABLE_JOB; not Dreamer; no PASS |
| 2026-09-09 17:58:46 JST | collect-other-1730-resume | completed | worker-3 | EXIT:3 NO_RUNNABLE_JOB unfinished 0; 25 requests; 16 cargo complete; not isomorphic R1 |
| 2026-09-09 17:58:46 JST | other-eco-review-remaining | started | worker-3 | screen remaining cargo issues from 1730-other; HOLD not PASS |
| 2026-09-09 17:59:44 JST | other-eco-review-remaining | completed | worker-3 | 10 cargo PRs HOLD (repair/feature); all 16 roots screened; no PASS; not Dreamer |
| 2026-09-09 18:00:14 JST | host-refute-14591-911 | started | worker-3 | pytest 9.1.1 on 14591 public snippet; HOLD; not Dreamer; not isomorphic R1 |
| 2026-09-09 18:00:18 JST | host-refute-14591-911 | completed | worker-3 | pytest 9.1.1 rc=0; HOLD no View; not Dreamer |
| 2026-09-09 18:01:55 JST | collect-expand-resume-200d | completed | worker-2 | EXIT:3 158 requests; refill worker-2 immediately; not isomorphic R1 |
| 2026-09-09 18:01:55 JST | collect-expand-resume-200e | started | worker-2 | resume a9328ef4 200/600 after 200d exit |
| 2026-09-09 18:02:32 JST | collect-expand-resume-200e | blocked | worker-2 | Corpus busy from overlapping status; retry immediately; not isomorphic R1 |
| 2026-09-09 18:02:32 JST | host-refute-14011-911 | started | worker-3 | pytest 9.1.1 on 14011 snippet; HOLD; not Dreamer |
| 2026-09-09 18:02:32 JST | collect-expand-resume-200e2 | started | worker-2 | retry resume a9328ef4 200/600 after lock free and RATE_WAIT passed |
| 2026-09-09 18:02:32 JST | host-refute-13885-911 | started | worker-1 | pytest 9.1.1 on 13885 snippet; HOLD; not Dreamer |
| 2026-09-09 18:02:32 JST | host-refute-14011-911 | completed | worker-3 | pytest 9.1.1 rc=1; HOLD no View; not Dreamer |
| 2026-09-09 18:02:32 JST | host-refute-13885-911 | completed | worker-1 | pytest 9.1.1 rc=0; HOLD no View; not Dreamer |
| 2026-09-09 18:03:03 JST | host-refute-13479-911 | started | worker-3 | pytest 9.1.1+freezegun on 13479 snippet; HOLD; not Dreamer |
| 2026-09-09 18:03:03 JST | host-refute-13479-911 | completed | worker-3 | pytest 9.1.1+freezegun rc=1; HOLD no View; not Dreamer |
| 2026-09-09 18:03:42 JST | expand-cargo-queue | completed | worker-1 | queued 7 expand cargo complete roots for next lock-free screen; HOLD pending; not Dreamer |
| 2026-09-09 18:06:14 JST | collect-expand-resume-200e2 | completed | worker-2 | EXIT:3 35 requests; refill immediately; not isomorphic R1 |
| 2026-09-09 18:06:14 JST | expand-cargo-screen | started | worker-1 | screen 7 expand cargo complete roots; HOLD not PASS |
| 2026-09-09 18:06:49 JST | collect-expand-resume-200f | started | worker-2 | resume a9328ef4 200/600 after 200e2 EXIT; not isomorphic R1 |
| 2026-09-09 18:06:49 JST | host-refute-14011-841 | started | worker-3 | pytest 8.4.1 on 14011 snippet; HOLD; not Dreamer |
| 2026-09-09 18:06:49 JST | expand-cargo-screen | blocked | worker-1 | body screen deferred: expand lock taken by 200f; HOLD pending; not PASS |
| 2026-09-09 18:06:49 JST | host-refute-14011-841 | completed | worker-3 | pytest 8.4.1 rc=1; HOLD no View; not Dreamer |
| 2026-09-09 18:07:22 JST | collect-expand-resume-200f | completed | worker-2 | NO_RUNNABLE_JOB unfinished 0; 0 requests this invocation; stop resuming expand; not isomorphic R1 |
| 2026-09-09 18:07:22 JST | expand-cargo-screen | started | worker-1 | lock free; screen 7 expand cargo complete roots; HOLD not PASS |
| 2026-09-09 18:07:24 JST | expand-cargo-screen | completed | worker-1 | 4 expand cargo HOLD; missing ['15834', '17148', '17326']; no PASS; not Dreamer |
| 2026-09-09 18:07:44 JST | expand-cargo-screen-rest | completed | worker-3 | remaining expand cargo HOLD n=3; no PASS; not Dreamer |
| 2026-09-09 18:08:08 JST | pytest-expand-more-screen | started | worker-2 | screen additional expand pytest complete issues; HOLD not PASS |
| 2026-09-09 18:08:13 JST | pytest-expand-more-screen | completed | worker-2 | 8 more pytest HOLD; no PASS; not Dreamer |
| 2026-09-09 18:08:37 JST | pytest-expand-screen-batch2 | started | worker-1 | screen remaining complete pytest issues with snippets; HOLD not PASS; not isomorphic R1 |
| 2026-09-09 18:08:39 JST | host-reconstitute-13754 | started | worker-3 | pytest --setup-plan on 13754 public snippet; HOLD no View; not Dreamer |
| 2026-09-09 18:08:40 JST | host-reconstitute-13754 | completed | worker-3 | 13754 setup-plan rc=0 run rc=0; HOLD no View |
| 2026-09-09 18:10:07 JST | pytest-expand-screen-batch2 | completed | worker-1 | 8 pytest HOLD already recorded in prior batch; no PASS; not isomorphic R1 |
