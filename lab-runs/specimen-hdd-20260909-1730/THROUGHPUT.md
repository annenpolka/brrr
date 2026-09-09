# Throughput

Vacant inference slots take the next ready job. Clock milestones are deadlines.
R1/test waits register a handle and free the slot. No isomorphic-Dream filler.

Updated: 2026-09-10 08:30:29 JST

Jobs recorded: 2718
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
| 2026-09-09 18:11:36 JST | host-refute-13754-841 | started | worker-3 | 13754 --setup-plan on pytest 8.4.1; HOLD; not Dreamer; not isomorphic R1 |
| 2026-09-09 18:11:36 JST | pytest-snippet-screen | started | worker-1 | screen next unreviewed pytest complete issues for public snippets; HOLD not PASS |
| 2026-09-09 18:11:36 JST | host-refute-13754-901 | started | worker-2 | 13754 --setup-plan on pytest 9.0.1; HOLD; not Dreamer |
| 2026-09-09 18:12:15 JST | host-refute-13754-841 | completed | worker-3 | 13754 setup-plan 8.4.1 rc=0 same as 9.1.1; HOLD no View |
| 2026-09-09 18:12:15 JST | host-refute-13754-901 | completed | worker-2 | 13754 setup-plan 9.0.1 rc=0 same as 9.1.1; HOLD no View |
| 2026-09-09 18:12:22 JST | pytest-snippet-screen | completed | worker-1 | 10 pytest HOLD; snippet_hits=[]; no PASS; not isomorphic R1 |
| 2026-09-09 18:12:43 JST | pytest-likely-snippet-screen | started | worker-2 | screen likely-bug pytest issues 14095/14101/14436/14683/14700/13925; HOLD not PASS |
| 2026-09-09 18:12:45 JST | pytest-likely-snippet-screen | completed | worker-2 | 2 HOLD; snippets=[]; no PASS; not isomorphic R1 |
| 2026-09-09 18:13:03 JST | snippet-inventory | started | worker-3 | inventory dumped issue JSON for python snippets not yet reconstituted |
| 2026-09-09 18:13:03 JST | snippet-inventory | completed | worker-3 | snippet issues 18; pending reconstitution listed; not isomorphic R1 |
| 2026-09-09 18:13:57 JST | host-reconstitute-14095 | started | worker-1 | 14095 class vs module fixture override snippet; HOLD; not Dreamer |
| 2026-09-09 18:13:57 JST | host-reconstitute-13965 | started | worker-2 | 13965 subTest N=1 snippet; HOLD; not Dreamer |
| 2026-09-09 18:13:58 JST | host-reconstitute-14095 | completed | worker-1 | 14095 9.0.1 rc=1 9.1.1 rc=1; HOLD no View |
| 2026-09-09 18:13:58 JST | host-reconstitute-13965 | completed | worker-2 | 13965 N=1 9.0.1 rc=0 9.1.1 rc=0; HOLD no View |
| 2026-09-09 18:14:33 JST | review-14101-feature | completed | worker-3 | 14101 subtest xfail is a feature request; HOLD; no View; not isomorphic R1 |
| 2026-09-09 18:15:32 JST | host-reconstitute-14775 | started | worker-1 | 14775 class fixture -Werror snippet; HOLD; not Dreamer |
| 2026-09-09 18:15:32 JST | host-reconstitute-14253 | started | worker-1 | 14253 log_cli_level int pyproject; HOLD; not Dreamer |
| 2026-09-09 18:15:32 JST | host-reconstitute-14092 | started | worker-1 | 14092 tmp_path_retention_count int; HOLD; not Dreamer |
| 2026-09-09 18:15:32 JST | host-reconstitute-14650 | started | worker-1 | 14650 strict_parametrization_ids snippet; HOLD; not Dreamer |
| 2026-09-09 18:15:32 JST | host-reconstitute-14094 | started | worker-1 | 14094 monkeypatch delitem raising=False snippet; HOLD; not Dreamer |
| 2026-09-09 18:15:32 JST | host-reconstitute-13925 | started | worker-1 | 13925 empty-string discovery layout; HOLD; not Dreamer |
| 2026-09-09 18:16:07 JST | host-reconstitute-14412 | started | worker-1 | 14412 subtest times; HOLD; not Dreamer; not isomorphic R1 |
| 2026-09-09 18:16:07 JST | host-reconstitute-14431 | started | worker-2 | 14431 add() test; HOLD not a cache bug; not Dreamer |
| 2026-09-09 18:16:07 JST | host-reconstitute-14514 | started | worker-3 | 14514 foo.test.py collection; HOLD feature; not Dreamer |
| 2026-09-09 18:16:08 JST | host-reconstitute-14412 | completed | worker-1 | 14412 rc=0; HOLD no View |
| 2026-09-09 18:16:08 JST | host-reconstitute-14431 | completed | worker-2 | 14431 rc=0; HOLD not a cache bug |
| 2026-09-09 18:16:08 JST | host-reconstitute-14514 | completed | worker-3 | 14514 collect rc=2; HOLD feature |
| 2026-09-09 18:17:08 JST | host-reconstitute-13925 | completed | worker-1 | harvested scheduler outputs; HOLD no View; rcs=['pytest841.rc:0', 'pytest901.rc:2', 'pytest911.rc:2'] |
| 2026-09-09 18:17:08 JST | host-reconstitute-14092 | completed | worker-1 | harvested scheduler outputs; HOLD no View; rcs=['pytest901.rc:3', 'pytest911.rc:3'] |
| 2026-09-09 18:17:08 JST | host-reconstitute-14094 | completed | worker-1 | harvested scheduler outputs; HOLD no View; rcs=['pytest901.rc:1', 'pytest911.rc:1'] |
| 2026-09-09 18:17:08 JST | host-reconstitute-14253 | completed | worker-1 | harvested scheduler outputs; HOLD no View; rcs=['pytest901.rc:3', 'pytest911.rc:3'] |
| 2026-09-09 18:17:08 JST | host-reconstitute-14650 | completed | worker-1 | harvested scheduler outputs; HOLD no View; rcs=['pytest910.rc:2', 'pytest911.rc:2'] |
| 2026-09-09 18:17:08 JST | host-reconstitute-14775 | completed | worker-1 | harvested scheduler outputs; HOLD no View; rcs=['pytest841.rc:0', 'pytest901.rc:0', 'pytest911.rc:1'] |
| 2026-09-09 18:17:08 JST | collect-pilot-expand-resume | completed | worker-2 | superseded by 200/200b/200c/200d/200e2/200f; expand now NO_RUNNABLE_JOB |
| 2026-09-09 18:17:08 JST | collect-pilot-expand-resume-200c | completed | worker-2 | EXIT:3 RATE_WAIT earlier; later 200d/200e2/200f ran |
| 2026-09-09 18:17:49 JST | host-reconstitute-14004 | started | worker-1 | 14004 nested autouse conftest; HOLD; not Dreamer |
| 2026-09-09 18:17:49 JST | host-reconstitute-14800 | started | worker-2 | 14800 lazy fixture skip; HOLD; not Dreamer |
| 2026-09-09 18:17:49 JST | review-14683-nimbus | started | worker-3 | 14683 needs nimbus/xarray; HOLD no reconstitution; not Dreamer |
| 2026-09-09 18:17:50 JST | host-reconstitute-14004 | completed | worker-1 | 14004 rc=0; HOLD no View |
| 2026-09-09 18:17:50 JST | host-reconstitute-14800 | completed | worker-2 | 14800 rc=1; HOLD no View |
| 2026-09-09 18:17:50 JST | review-14683-nimbus | completed | worker-3 | 14683 nimbus/xarray not reconstituted; HOLD; not Dreamer |
| 2026-09-09 18:19:55 JST | host-reconstitute-13882 | started | worker-1 | 13882 class-scoped fixture on subclass; HOLD; not Dreamer; not isomorphic R1 |
| 2026-09-09 18:19:55 JST | review-14436-fragment | started | worker-2 | 14436 caplog KeyError is HA fragment; HOLD no View |
| 2026-09-09 18:19:55 JST | review-14635-ha | started | worker-3 | 14635 Home Assistant tree; HOLD no View |
| 2026-09-09 18:19:55 JST | host-reconstitute-13882 | completed | worker-1 | 13882 rc=0; HOLD no View |
| 2026-09-09 18:19:55 JST | review-14436-fragment | completed | worker-2 | 14436 HA fragment HOLD; no View; not Dreamer |
| 2026-09-09 18:19:55 JST | review-14635-ha | completed | worker-3 | 14635 HA tree HOLD; no View; not Dreamer |
| 2026-09-09 18:20:25 JST | host-reconstitute-record | completed | coordinator | RESULT.md+HOLD table for 14775/13925/14253/14092/14650/14094; no PASS; no isomorphic R1; expand NO_RUNNABLE_JOB |
| 2026-09-09 18:20:29 JST | pytest-screen-batch3 | started | worker-1 | next unreviewed pytest complete issues; HOLD not PASS; not isomorphic R1 |
| 2026-09-09 18:20:29 JST | pytest-screen-batch3b | started | worker-2 | second slice of unreviewed pytest; HOLD not PASS |
| 2026-09-09 18:20:29 JST | snippet-pending-index | started | worker-3 | refresh pending snippet reconstitution list |
| 2026-09-09 18:20:38 JST | pytest-screen-batch3 | completed | worker-1 | 11 HOLD; snippets=[]; no PASS |
| 2026-09-09 18:20:38 JST | pytest-screen-batch3b | completed | worker-2 | paired with batch3; no PASS |
| 2026-09-09 18:20:38 JST | snippet-pending-index | completed | worker-3 | pending snippets ['14683', '14436', '14101', '14635']; not isomorphic R1 |
| 2026-09-09 18:21:05 JST | pytest-screen-batch4 | started | worker-1 | continue unreviewed pytest complete; HOLD not PASS; not isomorphic R1 |
| 2026-09-09 18:21:05 JST | review-14210-fix13885 | started | worker-2 | 14210 PR may fix 13885; HOLD as repair/正解; not Dreamer |
| 2026-09-09 18:21:05 JST | heartbeat-throughput | started | worker-3 | refresh throughput and heartbeat |
| 2026-09-09 18:21:11 JST | pytest-screen-batch4 | completed | worker-1 | 7 more pytest dumped HOLD; no PASS |
| 2026-09-09 18:21:11 JST | review-14210-fix13885 | completed | worker-2 | 14210 is a repair PR for skip+autouse; HOLD 正解; not Dreamer |
| 2026-09-09 18:21:11 JST | heartbeat-throughput | completed | worker-3 | throughput recorded to scratch; scheduler armed |
| 2026-09-09 18:24:18 JST | pytest-screen-batch5 | started | worker-1 | next unreviewed pytest complete; HOLD not PASS; not isomorphic R1 |
| 2026-09-09 18:24:18 JST | pytest-screen-batch5b | started | worker-2 | paired pytest dump HOLD |
| 2026-09-09 18:24:18 JST | host-refute-13885-14210 | started | worker-3 | 13885 skipIf+autouse vs 14210 repair PR note; HOLD 正解 off Dreamer |
| 2026-09-09 18:24:26 JST | pytest-screen-batch5 | completed | worker-1 | 7 pytest dumped HOLD; snippets=['14447']; no PASS |
| 2026-09-09 18:24:26 JST | pytest-screen-batch5b | completed | worker-2 | paired with batch5; no PASS |
| 2026-09-09 18:24:26 JST | host-refute-13885-14210 | completed | worker-3 | 14210 repair PR HOLD 正解; 13885 実機 already recorded; not Dreamer |
| 2026-09-09 18:25:07 JST | host-reconstitute-14447 | started | worker-1 | 14447 walrus assert rewrite 3 tests; HOLD 正解 off Dreamer |
| 2026-09-09 18:25:07 JST | host-reconstitute-14447-901 | started | worker-2 | 14447 on pytest 9.0.1; HOLD |
| 2026-09-09 18:25:07 JST | hold-14447-sha | started | worker-3 | record 14447 as 正解 HOLD; SHAs not on Dreamer channel |
| 2026-09-09 18:25:08 JST | host-reconstitute-14447 | completed | worker-1 | 14447 9.1.1 rc=1; HOLD 正解 off Dreamer |
| 2026-09-09 18:25:08 JST | host-reconstitute-14447-901 | completed | worker-2 | 14447 9.0.1 rc=1; HOLD |
| 2026-09-09 18:25:08 JST | hold-14447-sha | completed | worker-3 | 14447 正解 HOLD; SHAs not on Dreamer channel |
| 2026-09-09 18:27:22 JST | pytest-screen-batch6 | started | worker-1 | next unreviewed pytest complete issues; HOLD not PASS; not isomorphic R1 |
| 2026-09-09 18:27:22 JST | pytest-screen-batch6b | started | worker-2 | paired pytest dump HOLD |
| 2026-09-09 18:27:22 JST | host-verify-pending-snippets | started | worker-3 | reconstitute leftover public snippets if any; HOLD no View; not Dreamer |
| 2026-09-09 18:30:35 JST | pytest-screen-batch6 | completed | worker-1 | 36 remaining pytest complete roots HOLD; no PASS; not isomorphic R1 |
| 2026-09-09 18:30:35 JST | pytest-screen-batch6b | completed | worker-2 | paired dump of leftover pytest; no PASS |
| 2026-09-09 18:30:35 JST | host-verify-pending-snippets | completed | worker-3 | pending 14683/14436/14101/14635 still HOLD without extra trees; leftover pytest snippets queued |
| 2026-09-09 18:30:35 JST | host-reconstitute-14819 | started | worker-1 | 14819 chained comparison short-circuit snippet; HOLD no View; not Dreamer |
| 2026-09-09 18:30:35 JST | host-reconstitute-14820 | started | worker-2 | 14820 assertion rewrite rebinds name; HOLD no View; not Dreamer |
| 2026-09-09 18:30:35 JST | host-reconstitute-14971 | started | worker-3 | 14971 nested conftest file-arg interleave; HOLD no View; not Dreamer |
| 2026-09-09 18:31:48 JST | host-reconstitute-5203 | started | worker-1 | 5203 module fixture override snippet; HOLD; not Dreamer |
| 2026-09-09 18:31:48 JST | host-reconstitute-2043 | started | worker-1 | 2043 indirect params overridden fixture; HOLD; not Dreamer |
| 2026-09-09 18:31:48 JST | host-reconstitute-14640 | started | worker-1 | 14640 CLI order shared conftest; HOLD; no fix plugin; not Dreamer |
| 2026-09-09 18:31:48 JST | host-reconstitute-13784 | started | worker-1 | 13784 capteesys -s snippet as written; HOLD; not Dreamer |
| 2026-09-09 18:32:19 JST | host-reconstitute-14819 | completed | worker-1 | 14819 8.4.1/9.0.1/9.1.1 rc=1 both tests fail (no short-circuit); HOLD no View |
| 2026-09-09 18:32:19 JST | host-reconstitute-14820 | completed | worker-2 | 14820 8.4.1/9.0.1/9.1.1 rc=1 left operand 99==0; HOLD no View |
| 2026-09-09 18:32:19 JST | host-reconstitute-14971 | completed | worker-3 | 14971 8.4.1/9.0.1 3 pass; 9.1.1 nested_fixture missing on test_b; HOLD no View |
| 2026-09-09 18:32:19 JST | host-reconstitute-14691 | started | worker-1 | 14691 classmethod class-scoped fixture; HOLD no View; not Dreamer |
| 2026-09-09 18:32:19 JST | host-reconstitute-14445 | started | worker-2 | 14445 walrus duplicate eval; HOLD no View; not Dreamer |
| 2026-09-09 18:32:19 JST | host-reconstitute-13784 | started | worker-3 | 13784 capteesys -s doubled prints; HOLD no View; not Dreamer |
| 2026-09-09 18:33:39 JST | host-reconstitute-5203 | completed | worker-1 | 5203 8.4.1/9.0.1/9.1.1 rc=1 TestB 8==6; HOLD no View |
| 2026-09-09 18:33:39 JST | host-reconstitute-2043 | completed | worker-1 | 2043 8.4.1 collect err; 9.0.1 pass; 9.1.0 dup param; 9.1.1 pass; HOLD no View |
| 2026-09-09 18:33:39 JST | host-reconstitute-14640 | completed | worker-1 | 14640 9.1.1 interleaved shared missing; sorted 3 pass; no fix plugin; HOLD no View |
| 2026-09-09 18:33:39 JST | host-reconstitute-13784 | completed | worker-1 | 13784 8.4.1 stdout doubled; 9.1.1 once; HOLD no View |
| 2026-09-09 18:34:29 JST | host-reconstitute-14691 | completed | worker-1 | 14691 8.4.1/9.0.1/9.1.1 fixture sample not found; HOLD no View |
| 2026-09-09 18:34:29 JST | host-reconstitute-14445 | completed | worker-2 | 14445 8.4.1/9.0.1/9.0.3/9.1.1 rc=1 walrus double-eval; HOLD no View |
| 2026-09-09 18:34:29 JST | host-reconstitute-13784 | completed | worker-3 | 13784 8.4.1 stdout doubled; 9.1.1 once; HOLD no View |
| 2026-09-09 18:34:29 JST | host-reconstitute-14737 | started | worker-1 | 14737 package pytestmark skip; HOLD no View; not Dreamer |
| 2026-09-09 18:34:29 JST | host-refute-14445-plain | started | worker-2 | 14445 and 14819 --assert=plain vs rewrite; HOLD; not Dreamer |
| 2026-09-09 18:34:29 JST | host-reconstitute-14048 | started | worker-3 | 14048 --pyargs amodule.tests mini; HOLD no View; not Dreamer |
| 2026-09-09 18:36:30 JST | host-reconstitute-14737 | completed | worker-1 | 14737 8.4.1/9.0.1/9.1.1 skip in __init__.py does not apply; HOLD no View |
| 2026-09-09 18:36:30 JST | host-refute-14445-plain | completed | worker-2 | 14445 9.1.1 --assert=plain 2 pass; 14819 plain AssertionError not ZeroDivision; HOLD no View |
| 2026-09-09 18:36:30 JST | host-reconstitute-14048 | completed | worker-3 | 14048 --pyargs 8.4.1/9.1.1 rc=4 missing __init__.py; HOLD no View |
| 2026-09-09 18:36:30 JST | host-refute-14820-plain | started | worker-1 | 14820 --assert=plain vs rewrite; HOLD; not Dreamer |
| 2026-09-09 18:36:30 JST | host-refute-14048-init | started | worker-2 | 14048 --pyargs after adding tests/__init__.py; HOLD; not Dreamer |
| 2026-09-09 18:36:30 JST | throughput-audit-1834 | started | worker-3 | append scratch throughput audit; scheduler still 15m; not isomorphic R1 |
| 2026-09-09 18:37:06 JST | host-refute-14820-plain | completed | worker-1 | 14820 9.1.1 --assert=plain 2 pass; rewrite was 99==0; HOLD no View |
| 2026-09-09 18:37:06 JST | host-refute-14048-init | completed | worker-2 | 14048 --pyargs with tests/__init__.py 8.4.1/9.1.1 1 pass; HOLD no View |
| 2026-09-09 18:37:06 JST | throughput-audit-1834 | completed | worker-3 | scratch throughput-audit appended; idle_gaps 0; scheduler armed; not isomorphic R1 |
| 2026-09-09 18:37:06 JST | verify-run-gates-3 | started | worker-1 | re-run shipped 25 run-gate tests into scratch; not Dreamer |
| 2026-09-09 18:37:06 JST | verify-runpair-3 | started | worker-2 | re-run tests.test_runpair 12 into scratch; existing main op; not a new candidate |
| 2026-09-09 18:37:06 JST | gate-tick-1836 | started | worker-3 | clock_gate + r1_budget gate; no isomorphic R1; scheduler confirm |
| 2026-09-09 18:37:57 JST | verify-run-gates-3 | completed | worker-1 | tests.test_hdd_run_20260909_1730 25 OK (run 3); not Dreamer |
| 2026-09-09 18:37:57 JST | verify-runpair-3 | completed | worker-2 | tests.test_runpair 12 OK (run 3); existing main op |
| 2026-09-09 18:37:57 JST | gate-tick-1836 | completed | worker-3 | operate/work; r1 remaining $16.0671; no isomorphic R1; scheduler armed |
| 2026-09-09 18:37:57 JST | verify-run-gates-4 | started | worker-1 | second 25-test run into scratch; not Dreamer |
| 2026-09-09 18:37:57 JST | verify-runpair-4 | started | worker-2 | second runpair 12 into scratch; existing main op |
| 2026-09-09 18:37:57 JST | hdd-status-1837 | started | worker-3 | hdd.py status case-001-a; do not re-init; not isomorphic R1 |
| 2026-09-09 18:37:57 JST | verify-run-gates-4 | completed | worker-1 | tests.test_hdd_run_20260909_1730 25 OK (run 4) |
| 2026-09-09 18:37:57 JST | verify-runpair-4 | completed | worker-2 | tests.test_runpair 12 OK (run 4) |
| 2026-09-09 18:37:57 JST | hdd-status-1837 | completed | worker-3 | trial case-001-a still THIN_WRAPPER stopped; no re-init |
| 2026-09-09 18:38:29 JST | host-refute-14819-native | started | worker-1 | native python vs pytest rewrite short-circuit; HOLD; not Dreamer |
| 2026-09-09 18:38:29 JST | hold-notes-14819-14820 | started | worker-2 | HOLD notes; 正解 off Dreamer; not PASS |
| 2026-09-09 18:38:29 JST | first-selection-refresh | started | worker-3 | HOLD extras still no PASS; leftover complete roots screened; not isomorphic R1 |
| 2026-09-09 18:38:46 JST | host-refute-14819-native | completed | worker-1 | native python AssertionError + boom not called; pytest rewrite ZeroDivision+boom; HOLD no View |
| 2026-09-09 18:38:46 JST | hold-notes-14819-14820 | completed | worker-2 | HOLD notes written; 正解 off Dreamer |
| 2026-09-09 18:38:46 JST | first-selection-refresh | completed | worker-3 | HOLD extras still 0 PASS; leftover complete screened |
| 2026-09-09 18:38:46 JST | host-refute-14820-native | started | worker-1 | native python vs pytest rewrite rebind; HOLD; not Dreamer |
| 2026-09-09 18:38:46 JST | result-refresh-14819 | started | worker-2 | add native python row to 14819 RESULT; HOLD |
| 2026-09-09 18:38:46 JST | throughput-audit-1838 | started | worker-3 | append scratch audit; scheduler armed 18:44; not isomorphic R1 |
| 2026-09-09 18:39:16 JST | host-refute-14820-native | completed | worker-1 | native python both pass; pytest rewrite 99==0; HOLD no View |
| 2026-09-09 18:39:16 JST | result-refresh-14819 | completed | worker-2 | 14819 RESULT native AssertionError boom not called; HOLD |
| 2026-09-09 18:39:16 JST | throughput-audit-1838 | completed | worker-3 | docs refreshed; scheduler 18:44; not isomorphic R1 |
| 2026-09-09 18:39:16 JST | host-refute-14737-conftest | started | worker-1 | 14737 pytestmark in conftest vs __init__; HOLD; not Dreamer |
| 2026-09-09 18:39:16 JST | host-refute-14737-module | started | worker-2 | 14737 pytestmark in test module; HOLD; not Dreamer |
| 2026-09-09 18:39:16 JST | throughput-audit-1839 | started | worker-3 | append audit; no isomorphic R1 |
| 2026-09-09 18:39:42 JST | host-refute-14737-conftest | completed | worker-1 | 14737 pytestmark in conftest 8.4.1/9.1.1 still fails; HOLD no View |
| 2026-09-09 18:39:42 JST | host-refute-14737-module | completed | worker-2 | 14737 pytestmark in test module 9.1.1 1 skipped; HOLD no View |
| 2026-09-09 18:39:42 JST | throughput-audit-1839 | completed | worker-3 | 14737 control recorded; not isomorphic R1 |
| 2026-09-09 18:39:42 JST | host-refute-14691-no-classmethod | started | worker-1 | 14691 class fixture without classmethod; HOLD; not Dreamer |
| 2026-09-09 18:39:42 JST | host-refute-14691-staticmethod | started | worker-2 | 14691 staticmethod fixture; HOLD; not Dreamer |
| 2026-09-09 18:39:42 JST | throughput-audit-1839b | started | worker-3 | append audit; scheduler 18:44; not isomorphic R1 |
| 2026-09-09 18:40:00 JST | host-refute-14691-no-classmethod | completed | worker-1 | 14691 without classmethod 8.4.1/9.1.1 1 pass; HOLD no View |
| 2026-09-09 18:40:00 JST | host-refute-14691-staticmethod | completed | worker-2 | 14691 staticmethod fixture 9.1.1 1 pass; HOLD no View |
| 2026-09-09 18:40:00 JST | throughput-audit-1839b | completed | worker-3 | 14691 classmethod is the failing combo; not isomorphic R1 |
| 2026-09-09 18:40:00 JST | host-refute-14971-sorted | started | worker-1 | 14971 sorted file args vs interleaved; HOLD; not Dreamer |
| 2026-09-09 18:40:00 JST | host-refute-14971-dir | started | worker-2 | 14971 pytest tests/ directory collect; HOLD; not Dreamer |
| 2026-09-09 18:40:00 JST | throughput-audit-1840 | started | worker-3 | append audit; scheduler 18:44; not isomorphic R1 |
| 2026-09-09 18:40:23 JST | host-refute-14971-sorted | completed | worker-1 | 14971 9.1.1 sorted args 3 pass; interleaved was the fail; HOLD no View |
| 2026-09-09 18:40:23 JST | host-refute-14971-dir | completed | worker-2 | 14971 pytest tests/ 8.4.1/9.1.1 3 pass; HOLD no View |
| 2026-09-09 18:40:23 JST | throughput-audit-1840 | completed | worker-3 | 14971 interleaved-only; not isomorphic R1 |
| 2026-09-09 18:40:23 JST | host-refute-13784-nocap | started | worker-1 | 13784 -s without capteesys; HOLD; not Dreamer |
| 2026-09-09 18:40:23 JST | host-refute-13784-nos | started | worker-2 | 13784 capteesys without -s; HOLD; not Dreamer |
| 2026-09-09 18:40:23 JST | throughput-audit-1840b | started | worker-3 | append audit; scheduler 18:44; not isomorphic R1 |
| 2026-09-09 18:40:42 JST | host-refute-13784-nocap | completed | worker-1 | 13784 -s without capteesys stdout once on 8.4.1/9.1.1; HOLD no View |
| 2026-09-09 18:40:42 JST | host-refute-13784-nos | completed | worker-2 | 13784 capteesys without -s quiet; HOLD no View |
| 2026-09-09 18:40:42 JST | throughput-audit-1840b | completed | worker-3 | 13784 doubling needs capteesys+-s on 8.4.1; not isomorphic R1 |
| 2026-09-09 18:40:42 JST | host-refute-14445-native | started | worker-1 | 14445 native python vs rewrite; HOLD; not Dreamer |
| 2026-09-09 18:40:42 JST | docs-heartbeat-1840 | started | worker-2 | refresh heartbeat/STATE; HOLD no PASS |
| 2026-09-09 18:40:42 JST | scheduler-confirm-1840 | started | worker-3 | confirm 01a085570c447273a54294de2d99bfcf armed; not isomorphic R1 |
| 2026-09-09 18:41:07 JST | host-refute-14445-native | completed | worker-1 | 14445 native python both pass count==3; rewrite 6==3; HOLD no View |
| 2026-09-09 18:41:07 JST | docs-heartbeat-1840 | completed | worker-2 | heartbeat/STATE refreshed; HOLD no PASS |
| 2026-09-09 18:41:07 JST | scheduler-confirm-1840 | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf still 15m next ~18:44 JST |
| 2026-09-09 18:41:07 JST | snippet-pending-refresh | started | worker-1 | tree-only 14683/14436/14101/14635/14841 remain HOLD; not isomorphic R1 |
| 2026-09-09 18:41:07 JST | contamination-1837b | started | worker-2 | contamination still 0 on public bundle/seed/outbox |
| 2026-09-09 18:41:07 JST | jobs-rewrite-1841 | started | worker-3 | rewrite THROUGHPUT.md; idle_gaps 0; not isomorphic R1 |
| 2026-09-09 18:41:07 JST | snippet-pending-refresh | completed | worker-1 | tree-only remain HOLD; no PASS minted |
| 2026-09-09 18:41:07 JST | contamination-1837b | completed | worker-2 | contamination clean; FIRST_SELECTION does not relax |
| 2026-09-09 18:41:07 JST | jobs-rewrite-1841 | completed | worker-3 | THROUGHPUT rewritten; jobs=230 idle_gaps=0 |
| 2026-09-09 18:41:36 JST | pilot-review-controls | started | worker-1 | PILOT_EXPAND_REVIEW control rows for 14737/14691/14971/13784; HOLD not PASS |
| 2026-09-09 18:41:36 JST | unreviewed-zero-check | started | worker-2 | complete pytest leftover 36 and uv 8 all have review JSON; no PASS |
| 2026-09-09 18:41:36 JST | gate-tick-1841 | started | worker-3 | clock still operate/work; no isomorphic R1 |
| 2026-09-09 18:41:37 JST | pilot-review-controls | completed | worker-1 | control rows recorded; HOLD not PASS |
| 2026-09-09 18:41:37 JST | unreviewed-zero-check | completed | worker-2 | leftover complete pytest 36 and uv 8 all dumped HOLD |
| 2026-09-09 18:41:37 JST | gate-tick-1841 | completed | worker-3 | operate/work; hard_end 09:00 not extended; no isomorphic R1 |
| 2026-09-09 18:42:11 JST | host-matrix-14971-910 | started | worker-1 | 14971 on pytest 9.1.0 interleaved; HOLD; not Dreamer |
| 2026-09-09 18:42:11 JST | host-matrix-14819-910 | started | worker-2 | 14819 on pytest 9.0.3 and 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:42:11 JST | host-matrix-14820-910 | started | worker-3 | 14820 on pytest 9.0.3 and 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:42:34 JST | host-matrix-14971-910 | completed | worker-1 | 14971 9.0.3 3 pass; 9.1.0 already nested_fixture miss; HOLD no View |
| 2026-09-09 18:42:34 JST | host-matrix-14819-910 | completed | worker-2 | 14819 9.0.3/9.1.0 rc=1 same rewrite fail; HOLD no View |
| 2026-09-09 18:42:34 JST | host-matrix-14820-910 | completed | worker-3 | 14820 9.0.3/9.1.0 rc=1 99==0; HOLD no View |
| 2026-09-09 18:42:34 JST | hold-14841-note | started | worker-1 | 14841 multiprocessing+pytester HOLD no reconstitution; not Dreamer |
| 2026-09-09 18:42:34 JST | uv-complete-confirm | started | worker-2 | uv 17/17 complete HOLD; partial 19603/19770 not PASS |
| 2026-09-09 18:42:34 JST | scheduler-prefire-1843 | started | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf still armed; not isomorphic R1 |
| 2026-09-09 18:42:34 JST | hold-14841-note | completed | worker-1 | 14841 HOLD note; no View |
| 2026-09-09 18:42:34 JST | uv-complete-confirm | completed | worker-2 | uv complete 17 HOLD; 2 partial remain partial |
| 2026-09-09 18:42:34 JST | scheduler-prefire-1843 | completed | worker-3 | armed until 18:44 JST fire; idle_gaps 0 |
| 2026-09-09 18:42:53 JST | result-matrix-14737 | started | worker-1 | 14737 9.0.3/9.1.0 also fail skip; HOLD no View |
| 2026-09-09 18:42:53 JST | result-matrix-14691 | started | worker-2 | 14691 9.0.3/9.1.0 fixture sample not found; HOLD no View |
| 2026-09-09 18:42:53 JST | clock-pre-1844 | started | worker-3 | clock operate/work; scheduler about to fire; not isomorphic R1 |
| 2026-09-09 18:42:53 JST | result-matrix-14737 | completed | worker-1 | 14737 RESULT versions recorded; HOLD |
| 2026-09-09 18:42:53 JST | result-matrix-14691 | completed | worker-2 | 14691 RESULT versions recorded; HOLD |
| 2026-09-09 18:42:53 JST | clock-pre-1844 | completed | worker-3 | operate/work; hard_end not extended; no isomorphic R1 |
| 2026-09-09 18:43:19 JST | handoff-scheduler-1844 | started | worker-1 | next ready is 15m vacancy tick; leftover tree-only HOLD; not isomorphic R1 |
| 2026-09-09 18:43:19 JST | scratch-audit-1843 | started | worker-2 | append throughput-audit; idle_gaps 0 |
| 2026-09-09 18:43:19 JST | no-resume-collect | started | worker-3 | expand/other remain NO_RUNNABLE_JOB; do not resume; HOLD not PASS |
| 2026-09-09 18:43:19 JST | handoff-scheduler-1844 | completed | worker-1 | scheduler 01a085570c447273a54294de2d99bfcf nextFire 18:44:29 JST; workers free for that tick |
| 2026-09-09 18:43:19 JST | scratch-audit-1843 | completed | worker-2 | throughput-audit appended; jobs>=257 idle_gaps 0 |
| 2026-09-09 18:43:19 JST | no-resume-collect | completed | worker-3 | no expand/other resume; consumer still 1 discovery 小規模試行 |
| 2026-09-09 18:45:38 JST | host-refute-14800-matrix | started | worker-1 | 14800 fixture execute _finalizers on 8.4.1/9.0.1/9.1.0/9.1.1; HOLD no View; not Dreamer |
| 2026-09-09 18:45:38 JST | host-reconstitute-14101 | started | worker-2 | 14101 subtest xfail_strict feature snippet; HOLD feature; not Dreamer |
| 2026-09-09 18:45:38 JST | host-refute-14004-matrix | started | worker-3 | 14004 nested autouse on 8.4.1/9.0.1; HOLD no View; not Dreamer |
| 2026-09-09 18:46:01 JST | host-reconstitute-14964 | started | worker-1 | 14964 interleaved file-arg autouse conftest; HOLD; not Dreamer |
| 2026-09-09 18:46:01 JST | hold-14608-sketch | started | worker-2 | 14608 nested addoption remains directory sketch; HOLD not fabricated |
| 2026-09-09 18:46:14 JST | host-refute-14800-matrix | completed | worker-1 | 14800 8.4.1/9.0.1 2 pass 1 skip; 9.1.0/9.1.1 _finalizers errors; HOLD no View |
| 2026-09-09 18:46:14 JST | host-reconstitute-14101 | completed | worker-2 | 14101 xfail_strict XPASS on 9.0.1/9.1.1; desired xfail= kwarg not a feature; HOLD |
| 2026-09-09 18:46:14 JST | host-refute-14004-matrix | completed | worker-3 | 14004 8.4.1/9.0.1/9.1.1 4 pass; HOLD no View |
| 2026-09-09 18:46:14 JST | host-refute-13882-matrix | started | worker-1 | 13882 subclass fixtures 8.4.1/9.0.1; HOLD no View; not Dreamer |
| 2026-09-09 18:46:14 JST | host-refute-14514-matrix | started | worker-2 | 14514 foo.test.py collect 8.4.1/9.0.1/9.1.1; HOLD feature; not Dreamer |
| 2026-09-09 18:46:14 JST | host-refute-14412-matrix | started | worker-3 | 14412 subtest times 8.4.1/9.0.1; HOLD; not Dreamer |
| 2026-09-09 18:47:01 JST | host-reconstitute-14964 | completed | worker-1 | 14964 9.1.1 interleaved test_b misses autouse; 8.4.1/9.0.1 both error; HOLD no View |
| 2026-09-09 18:47:01 JST | hold-14608-sketch | completed | worker-2 | 14608 nested addoption directory sketch only; not fabricated; HOLD no View |
| 2026-09-09 18:47:11 JST | host-refute-13882-matrix | completed | worker-1 | 13882 8.4.1/9.0.1/9.1.1 2 pass; does not reproduce reporter; HOLD no View |
| 2026-09-09 18:47:11 JST | host-refute-14514-matrix | completed | worker-2 | 14514 collect 8.4.1/9.0.1/9.1.1 rc=2 foo.test ImportError; HOLD feature |
| 2026-09-09 18:47:11 JST | host-refute-14412-matrix | completed | worker-3 | 14412 -q pass all; times capture queued; HOLD |
| 2026-09-09 18:47:11 JST | host-refute-14412-times | started | worker-1 | 14412 console_output_style=times 8.4.1/9.0.1/9.1.1; HOLD; not Dreamer |
| 2026-09-09 18:47:11 JST | host-refute-14095-841 | started | worker-2 | 14095 class fixture a vs module b on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:47:11 JST | host-refute-14431-matrix | started | worker-3 | 14431 add() 8.4.1/9.0.1; HOLD not a cache bug; not Dreamer |
| 2026-09-09 18:47:45 JST | host-refute-14412-times | completed | worker-1 | 14412 8.4.1 no times (ini section unread); 9.0.1/9.1.1 later subtests 0.000us; HOLD no View |
| 2026-09-09 18:47:45 JST | host-refute-14095-841 | completed | worker-2 | 14095 8.4.1 rc=1 assert 0==1 same as 9.x; HOLD no View |
| 2026-09-09 18:47:45 JST | host-refute-14431-matrix | completed | worker-3 | 14431 default collect 8.4.1/9.0.1 no tests; explicit path queued |
| 2026-09-09 18:47:45 JST | host-refute-14431-explicit | started | worker-1 | 14431 pytest test.py explicit 8.4.1/9.0.1/9.1.1; HOLD; not Dreamer |
| 2026-09-09 18:47:45 JST | host-refute-13965-841 | started | worker-2 | 13965 N=1 unittest subTest on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:47:45 JST | scheduler-confirm-1847 | started | worker-3 | confirm 01a085570c447273a54294de2d99bfcf after 18:44 fire; not isomorphic R1 |
| 2026-09-09 18:48:19 JST | host-refute-14431-explicit | completed | worker-1 | 14431 explicit test.py 8.4.1/9.0.1/9.1.1 1 pass; HOLD not a cache bug |
| 2026-09-09 18:48:19 JST | host-refute-13965-841 | completed | worker-2 | 13965 default collect 8.4.1 no tests; explicit path queued |
| 2026-09-09 18:48:19 JST | scheduler-confirm-1847 | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf nextFire 18:59:29 JST; still 15m |
| 2026-09-09 18:48:19 JST | host-refute-13965-explicit | started | worker-1 | 13965 pytest test.py 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:48:19 JST | host-refute-14253-841 | started | worker-2 | 14253 log_cli_level int on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:48:19 JST | host-refute-14092-841 | started | worker-3 | 14092 tmp_path_retention_count int on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:48:58 JST | host-refute-13965-explicit | completed | worker-1 | 13965 8.4.1 explicit test.py 1 pass; HOLD no View |
| 2026-09-09 18:48:58 JST | host-refute-14253-841 | completed | worker-2 | 14253 8.4.1 [tool.pytest] unread so dummy pass; ini_options queued |
| 2026-09-09 18:48:58 JST | host-refute-14092-841 | completed | worker-3 | 14092 8.4.1 [tool.pytest] unread dummy pass; ini_options queued |
| 2026-09-09 18:48:58 JST | host-refute-14253-ini-options | started | worker-1 | 14253 8.4.1 [tool.pytest.ini_options] int log_cli_level; HOLD; not Dreamer |
| 2026-09-09 18:48:58 JST | host-refute-14092-ini-options | started | worker-2 | 14092 8.4.1 [tool.pytest.ini_options] int retention; HOLD; not Dreamer |
| 2026-09-09 18:48:58 JST | host-refute-14650-901-841 | started | worker-3 | 14650 8.4.1/9.0.1 strict ids; HOLD; not Dreamer |
| 2026-09-09 18:50:22 JST | host-refute-14253-ini-options | completed | worker-1 | 14253 [tool.pytest] TypeError on pytest9; ini_options int rc=0; HOLD no View |
| 2026-09-09 18:50:22 JST | host-refute-14092-ini-options | completed | worker-2 | 14092 same [tool.pytest] vs ini_options split; HOLD no View |
| 2026-09-09 18:50:22 JST | host-refute-14650-901-841 | completed | worker-3 | 14650 8.4.1 2 pass; 9.0.1+ duplicate IDs rc=2; HOLD no View |
| 2026-09-09 18:50:22 JST | host-reconstitute-14148 | started | worker-1 | 14148 pytestconfig.cache with -p no:cacheprovider; HOLD; not Dreamer |
| 2026-09-09 18:50:22 JST | host-reconstitute-14608 | started | worker-2 | 14608 sibling addoption A/B sketch; HOLD; not Dreamer |
| 2026-09-09 18:50:22 JST | host-refute-14094-841 | started | worker-3 | 14094 Monkeypatch AttributeError on 8.4.1 too; HOLD; not Dreamer |
| 2026-09-09 18:50:44 JST | host-reconstitute-14148 | completed | worker-1 | 14148 -p no:cacheprovider AttributeError 8.4.1/9.1.1; default 9.1.1 pass; HOLD no View |
| 2026-09-09 18:50:44 JST | host-reconstitute-14608 | completed | worker-2 | 14608 pytest A --from-b unrecognized 8.4.1 and 9.1.1; A B pass; HOLD no View |
| 2026-09-09 18:50:44 JST | host-refute-14094-841 | completed | worker-3 | 14094 8.4.1 Monkeypatch AttributeError; HOLD no View |
| 2026-09-09 18:50:44 JST | host-refute-14608-cwdA | started | worker-1 | 14608 cwd=A pytest --from-b ../B; HOLD; not Dreamer |
| 2026-09-09 18:50:44 JST | docs-1844-tick | started | worker-2 | README/PILOT/heartbeat/STATE refresh; HOLD not PASS |
| 2026-09-09 18:50:44 JST | throughput-audit-1850 | started | worker-3 | append scratch audit; scheduler next 18:59; not isomorphic R1 |
| 2026-09-09 18:51:56 JST | host-refute-14608-cwdA | completed | worker-1 | 14608 cwd=A pytest --from-b ../B 8.4.1/9.1.1 1 pass; HOLD no View |
| 2026-09-09 18:51:56 JST | docs-1844-tick | completed | worker-2 | README/PILOT/heartbeat/STATE/STATUS refreshed; HOLD not PASS |
| 2026-09-09 18:51:56 JST | throughput-audit-1850 | completed | worker-3 | docs+host 実機 recorded; not isomorphic R1 |
| 2026-09-09 18:51:56 JST | host-refute-14447-841 | started | worker-1 | 14447 walrus rewrite on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:51:56 JST | contamination-1851 | started | worker-2 | contamination 0 public bundle/seed/outbox; FIRST_SELECTION does not relax |
| 2026-09-09 18:51:56 JST | worktree-check-1851 | started | worker-3 | no worktrees in run dir; no collect resume; not isomorphic R1 |
| 2026-09-09 18:52:38 JST | host-refute-14447-841 | completed | worker-1 | 14447 8.4.1 rc=1 3 failed same walrus rewrite; HOLD no View |
| 2026-09-09 18:52:38 JST | contamination-1851 | completed | worker-2 | contamination clean; FIRST_SELECTION does not relax |
| 2026-09-09 18:52:38 JST | worktree-check-1851 | completed | worker-3 | no worktrees in run dir; jobs rewritten; not isomorphic R1 |
| 2026-09-09 18:52:38 JST | host-refute-14591-841 | started | worker-1 | 14591 indirect parametrize on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:52:38 JST | host-refute-13754-run841 | started | worker-2 | 13754 pytest run (not only setup-plan) on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 18:52:38 JST | gate-tick-1852 | started | worker-3 | clock operate/work; r1 remaining; no isomorphic R1 |
| 2026-09-09 18:52:54 JST | host-refute-14591-841 | completed | worker-1 | 14591 8.4.1 4 passed; HOLD no View (9.1.0 still the collect error) |
| 2026-09-09 18:52:54 JST | host-refute-13754-run841 | completed | worker-2 | 13754 default collect no tests; explicit test.py queued |
| 2026-09-09 18:52:54 JST | gate-tick-1852 | completed | worker-3 | operate/work; r1 remaining $16.0671; no isomorphic R1 |
| 2026-09-09 18:52:54 JST | host-refute-13754-explicit | started | worker-1 | 13754 explicit test.py 8.4.1/9.0.1/9.1.1; HOLD; not Dreamer |
| 2026-09-09 18:52:54 JST | docs-14591-841 | started | worker-2 | 14591 RESULT 8.4.1 4 pass; HOLD no View |
| 2026-09-09 18:52:54 JST | throughput-audit-1853 | started | worker-3 | append audit; scheduler 18:59; not isomorphic R1 |
| 2026-09-09 18:53:21 JST | host-refute-13754-explicit | completed | worker-1 | 13754 explicit test.py 8.4.1/9.0.1/9.1.1 4 pass; HOLD no View |
| 2026-09-09 18:53:21 JST | docs-14591-841 | completed | worker-2 | 14591 8.4.1 4 pass recorded; HOLD no View |
| 2026-09-09 18:53:21 JST | throughput-audit-1853 | completed | worker-3 | audit appended; not isomorphic R1 |
| 2026-09-09 18:53:21 JST | host-refute-14447-plain841 | started | worker-1 | 14447 8.4.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 18:53:21 JST | hold-14101-note | started | worker-2 | HOLD-14101 feature note; 正解 off Dreamer |
| 2026-09-09 18:53:21 JST | scheduler-confirm-1853 | started | worker-3 | scheduler still 15m next 18:59 JST; not isomorphic R1 |
| 2026-09-09 18:53:44 JST | host-refute-14447-plain841 | completed | worker-1 | 14447 8.4.1 --assert=plain 3 pass; rewrite 3 fail; HOLD no View |
| 2026-09-09 18:53:44 JST | hold-14101-note | completed | worker-2 | HOLD-14101 written; feature not View |
| 2026-09-09 18:53:44 JST | scheduler-confirm-1853 | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf next 18:59:29 JST |
| 2026-09-09 18:53:44 JST | hold-14148-14608 | started | worker-1 | HOLD notes for 14148/14608; no View; not Dreamer |
| 2026-09-09 18:53:44 JST | scratch-clock-1853 | started | worker-2 | copy clock-gate-latest to scratch; not isomorphic R1 |
| 2026-09-09 18:53:44 JST | jobs-rewrite-1853 | started | worker-3 | THROUGHPUT rewrite; idle_gaps 0; not isomorphic R1 |
| 2026-09-09 18:53:44 JST | hold-14148-14608 | completed | worker-1 | HOLD-14148 and HOLD-14608 written; no PASS |
| 2026-09-09 18:53:44 JST | scratch-clock-1853 | completed | worker-2 | clock-gate-latest copied to scratch |
| 2026-09-09 18:53:44 JST | jobs-rewrite-1853 | completed | worker-3 | THROUGHPUT rewritten jobs=342 idle_gaps=0 |
| 2026-09-09 18:54:08 JST | host-refute-14148-901 | started | worker-1 | 14148 9.0.1 cache on/off; HOLD; not Dreamer |
| 2026-09-09 18:54:08 JST | host-refute-14608-901 | started | worker-2 | 14608 9.0.1 A vs A B --from-b; HOLD; not Dreamer |
| 2026-09-09 18:54:08 JST | host-refute-14591-901 | started | worker-3 | 14591 9.0.1 indirect parametrize; HOLD; not Dreamer |
| 2026-09-09 18:54:48 JST | host-refute-14148-901 | completed | worker-1 | 14148 9.0.1 cache on pass / off AttributeError; HOLD no View |
| 2026-09-09 18:54:48 JST | host-refute-14608-901 | completed | worker-2 | 14608 9.0.1 A unrecognized / A B pass; HOLD no View |
| 2026-09-09 18:54:48 JST | host-refute-14591-901 | completed | worker-3 | 14591 9.0.1 4 pass; HOLD no View |
| 2026-09-09 18:54:48 JST | host-refute-14775-910 | started | worker-1 | 14775 class fixture -Werror on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:54:48 JST | host-refute-14011-910 | started | worker-2 | 14011 inherited class fixture on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:54:48 JST | host-refute-13885-910 | started | worker-3 | 13885 skipIf+autouse on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:55:18 JST | host-refute-14775-910 | completed | worker-1 | 14775 9.1.0 2 pass 1 warning; 9.1.1 _finalizers; HOLD no View |
| 2026-09-09 18:55:18 JST | host-refute-14011-910 | completed | worker-2 | 14011 9.1.0 still both tests None; HOLD no View |
| 2026-09-09 18:55:18 JST | host-refute-13885-910 | completed | worker-3 | 13885 9.1.0 1 skipped like 9.1.1; HOLD no View |
| 2026-09-09 18:55:18 JST | host-refute-13479-910 | started | worker-1 | 13479 freezegun fixture ff on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:55:18 JST | host-refute-13925-910 | started | worker-2 | 13925 empty-string discovery on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:55:18 JST | throughput-audit-1855 | started | worker-3 | append audit; scheduler 18:59; not isomorphic R1 |
| 2026-09-09 18:55:58 JST | host-refute-13479-910 | completed | worker-1 | 13479 9.1.0+freezegun fixture ff not found; HOLD no View |
| 2026-09-09 18:55:58 JST | host-refute-13925-910 | completed | worker-2 | 13925 9.1.0 empty-string collect ZeroDivisionError; HOLD no View |
| 2026-09-09 18:55:58 JST | throughput-audit-1855 | completed | worker-3 | 13479/13925 9.1.0 recorded; not isomorphic R1 |
| 2026-09-09 18:55:58 JST | host-refute-14004-910 | started | worker-1 | 14004 nested autouse 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:55:58 JST | host-refute-13882-910 | started | worker-2 | 13882 subclass fixtures 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:55:58 JST | scheduler-confirm-1856 | started | worker-3 | scheduler next 18:59 JST; no isomorphic R1; no collect resume |
| 2026-09-09 18:56:22 JST | host-refute-14004-910 | completed | worker-1 | 14004 9.1.0 4 pass; HOLD no View |
| 2026-09-09 18:56:22 JST | host-refute-13882-910 | completed | worker-2 | 13882 9.1.0 2 pass; HOLD no View |
| 2026-09-09 18:56:23 JST | scheduler-confirm-1856 | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf next 18:59:29 JST; no isomorphic R1 |
| 2026-09-09 18:56:23 JST | host-refute-14431-910 | started | worker-1 | 14431 explicit test.py on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:56:23 JST | docs-1856 | started | worker-2 | heartbeat refresh; tree-only HOLD; not PASS |
| 2026-09-09 18:56:23 JST | handoff-1859 | started | worker-3 | workers free for 18:59 vacancy tick; no collect resume; no Dream 0004 |
| 2026-09-09 18:56:23 JST | host-refute-14431-910 | completed | worker-1 | 14431 9.1.0 explicit 1 pass; HOLD not a cache bug |
| 2026-09-09 18:56:23 JST | docs-1856 | completed | worker-2 | heartbeat updated; tree-only 14683/14436/14635/14841 HOLD |
| 2026-09-09 18:56:23 JST | handoff-1859 | completed | worker-3 | next scheduler fire 18:59:29 JST; idle_gaps 0; no isomorphic R1 |
| 2026-09-09 18:56:37 JST | host-refute-14095-910 | started | worker-1 | 14095 class vs module fixture on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:56:37 JST | host-refute-14447-910 | started | worker-2 | 14447 walrus rewrite on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:56:37 JST | host-refute-13965-910 | started | worker-3 | 13965 N=1 explicit test.py on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:56:59 JST | host-refute-14095-910 | completed | worker-1 | 14095 9.1.0 rc=1 0==1; HOLD no View |
| 2026-09-09 18:56:59 JST | host-refute-14447-910 | completed | worker-2 | 14447 9.1.0 rc=1 3 failed; HOLD no View |
| 2026-09-09 18:56:59 JST | host-refute-13965-910 | completed | worker-3 | 13965 9.1.0 N=1 pass; HOLD no View |
| 2026-09-09 18:56:59 JST | host-refute-14253-910 | started | worker-1 | 14253 [tool.pytest] int log_cli_level on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:56:59 JST | host-refute-14092-910 | started | worker-2 | 14092 [tool.pytest] int retention on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:56:59 JST | host-refute-14094-910 | started | worker-3 | 14094 Monkeypatch on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:57:25 JST | host-refute-14253-910 | completed | worker-1 | 14253 9.1.0 [tool.pytest] int TypeError rc=3; HOLD no View |
| 2026-09-09 18:57:25 JST | host-refute-14092-910 | completed | worker-2 | 14092 9.1.0 int TypeError rc=3; HOLD no View |
| 2026-09-09 18:57:25 JST | host-refute-14094-910 | completed | worker-3 | 14094 9.1.0 Monkeypatch AttributeError; HOLD no View |
| 2026-09-09 18:57:25 JST | host-refute-14101-910 | started | worker-1 | 14101 xfail_strict on 9.1.0; HOLD feature; not Dreamer |
| 2026-09-09 18:57:25 JST | host-refute-14608-910 | started | worker-2 | 14608 --from-b A on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 18:57:25 JST | handoff-1859b | started | worker-3 | next 18:59 vacancy tick; no Dream 0004; no collect resume; tree-only HOLD |
| 2026-09-09 18:57:25 JST | host-refute-14101-910 | completed | worker-1 | 14101 9.1.0 xfail_strict still XPASS/fail; HOLD feature |
| 2026-09-09 18:57:25 JST | host-refute-14608-910 | completed | worker-2 | 14608 9.1.0 pytest A --from-b unrecognized; HOLD no View |
| 2026-09-09 18:57:25 JST | handoff-1859b | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf next 18:59:29 JST; idle_gaps 0 |
| 2026-09-09 18:57:40 JST | contamination-1857 | started | worker-1 | contamination 0; FIRST_SELECTION does not relax; not isomorphic R1 |
| 2026-09-09 18:57:40 JST | worktree-check-1857 | started | worker-2 | no worktrees in run dir; tree-only HOLD; no collect resume |
| 2026-09-09 18:57:40 JST | pre-1859-tick | started | worker-3 | clock operate/work; scheduler next 18:59:29 JST; no Dream 0004 |
| 2026-09-09 18:57:40 JST | contamination-1857 | completed | worker-1 | contamination clean |
| 2026-09-09 18:57:40 JST | worktree-check-1857 | completed | worker-2 | no worktrees in run dir |
| 2026-09-09 18:57:40 JST | pre-1859-tick | completed | worker-3 | operate/work; 18:59 tick should take next non-Dream job |
| 2026-09-09 19:00:23 JST | host-reconstitute-14935 | started | worker-1 | 14935 two-project tmp_path retention layout; HOLD design; not Dreamer |
| 2026-09-09 19:00:23 JST | host-refute-14412-times910 | started | worker-2 | 14412 console_output_style=times on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:00:23 JST | host-refute-14640-910 | started | worker-3 | 14640 CASE1 interleaved on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:01:12 JST | host-reconstitute-14935 | completed | worker-1 | 14935 user-scoped pytest-of-<user> evicted proj-a after 4 proj-b runs; no .origin; HOLD design no View |
| 2026-09-09 19:01:12 JST | host-refute-14412-times910 | completed | worker-2 | 14412 times on 9.1.0 recorded; HOLD no View |
| 2026-09-09 19:01:12 JST | host-refute-14640-910 | completed | worker-3 | 14640 CASE1 9.1.0 shared missing like 9.1.1; CASE2 3 pass; HOLD no View |
| 2026-09-09 19:01:12 JST | host-refute-14935-841 | started | worker-1 | 14935 8.4.1 two-project tmp_path layout; HOLD; not Dreamer |
| 2026-09-09 19:01:12 JST | host-refute-14412-times901-done | started | worker-2 | confirm 14412 9.1.0 0.000us; HOLD |
| 2026-09-09 19:01:12 JST | hold-14877-note | started | worker-3 | 14877 profiler/pytester perf; HOLD no mini; not Dreamer |
| 2026-09-09 19:01:54 JST | host-reconstitute-14808 | started | worker-1 | 14808 addini string vs toml array; HOLD; not Dreamer |
| 2026-09-09 19:01:54 JST | host-reconstitute-14560 | started | worker-2 | 14560 dict-subclass parametrize KeyError; HOLD reconstructed from public description; not Dreamer |
| 2026-09-09 19:01:54 JST | hold-14613-feature | started | worker-3 | 14613 PYTEST_CACHE_DIR_BASE feature request; HOLD no mini |
| 2026-09-09 19:02:03 JST | host-refute-14935-841 | completed | worker-1 | 14935 8.4.1 same user-scoped eviction; no .origin; HOLD design no View |
| 2026-09-09 19:02:03 JST | host-refute-14412-times901-done | completed | worker-2 | 14412 9.1.0 later subtests 0.000us; HOLD no View |
| 2026-09-09 19:02:03 JST | hold-14877-note | completed | worker-3 | 14877 HOLD note written; no mini; not PASS |
| 2026-09-09 19:02:03 JST | host-refute-14935-901 | started | worker-1 | 14935 9.0.1 two-project tmp_path layout; HOLD; not Dreamer |
| 2026-09-09 19:02:03 JST | docs-1859-tick | started | worker-2 | README/heartbeat/STATE refresh; HOLD not PASS |
| 2026-09-09 19:02:03 JST | throughput-audit-1901 | started | worker-3 | append scratch audit; scheduler next 19:14; not isomorphic R1 |
| 2026-09-09 19:02:59 JST | host-refute-14935-901 | completed | worker-1 | 14935 9.0.1 user-scoped eviction; no .origin; HOLD design no View |
| 2026-09-09 19:02:59 JST | docs-1859-tick | completed | worker-2 | README/heartbeat/STATE/STATUS/PILOT refreshed; HOLD not PASS |
| 2026-09-09 19:02:59 JST | throughput-audit-1901 | completed | worker-3 | 18:59 tick recorded; not isomorphic R1 |
| 2026-09-09 19:02:59 JST | host-refute-14640-903 | started | worker-1 | 14640 CASE1 interleaved on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:02:59 JST | host-refute-14412-times903 | started | worker-2 | 14412 times on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:02:59 JST | host-refute-14935-910 | started | worker-3 | 14935 9.1.0 two-project layout; HOLD; not Dreamer |
| 2026-09-09 19:03:32 JST | host-refute-14640-903 | completed | worker-1 | 14640 CASE1 9.0.3 3 pass; miss starts 9.1.0; HOLD no View |
| 2026-09-09 19:03:32 JST | host-refute-14412-times903 | completed | worker-2 | 14412 9.0.3 later subtests 0.000us; HOLD no View |
| 2026-09-09 19:03:32 JST | host-refute-14935-910 | completed | worker-3 | 14935 9.1.0 user-scoped eviction; HOLD design no View |
| 2026-09-09 19:03:32 JST | host-refute-14964-903 | started | worker-1 | 14964 CASE1 interleaved on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:03:32 JST | host-refute-14964-910 | started | worker-2 | 14964 CASE1 interleaved on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:03:32 JST | host-refute-14800-903 | started | worker-3 | 14800 fixture execute on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:03:52 JST | host-refute-14964-903 | completed | worker-1 | 14964 CASE1 9.0.3 both tests ERROR guard; HOLD no View |
| 2026-09-09 19:03:52 JST | host-refute-14964-910 | completed | worker-2 | 14964 CASE1 9.1.0 test_b PASSES like 9.1.1; HOLD no View |
| 2026-09-09 19:03:52 JST | host-refute-14800-903 | completed | worker-3 | 14800 9.0.3 2 pass 1 skip; HOLD no View |
| 2026-09-09 19:03:52 JST | host-refute-14011-903 | started | worker-1 | 14011 inherited fixture on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:03:52 JST | host-refute-13885-903 | started | worker-2 | 13885 skipIf+autouse on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:03:52 JST | host-refute-14775-903 | started | worker-3 | 14775 class fixture -Werror on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:15 JST | host-refute-14011-903 | completed | worker-1 | 14011 9.0.3 both tests fail; HOLD no View |
| 2026-09-09 19:04:15 JST | host-refute-13885-903 | completed | worker-2 | 13885 9.0.3 autouse still fires rc=1; HOLD no View |
| 2026-09-09 19:04:15 JST | host-refute-14775-903 | completed | worker-3 | 14775 9.0.3 2 pass; HOLD no View |
| 2026-09-09 19:04:15 JST | host-refute-13925-903 | started | worker-1 | 13925 empty-string discovery on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:15 JST | host-refute-14101-903 | started | worker-2 | 14101 xfail_strict on 9.0.3; HOLD feature; not Dreamer |
| 2026-09-09 19:04:15 JST | host-refute-14608-903 | started | worker-3 | 14608 --from-b A on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:32 JST | host-refute-13925-903 | completed | worker-1 | 13925 9.0.3 empty-string collect error; HOLD no View |
| 2026-09-09 19:04:32 JST | host-refute-14101-903 | completed | worker-2 | 14101 9.0.3 xfail_strict 4 failed; HOLD feature |
| 2026-09-09 19:04:32 JST | host-refute-14608-903 | completed | worker-3 | 14608 9.0.3 --from-b A unrecognized; HOLD no View |
| 2026-09-09 19:04:32 JST | host-refute-14447-903 | started | worker-1 | 14447 walrus rewrite on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:32 JST | host-refute-14095-903 | started | worker-2 | 14095 class vs module fixture on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:32 JST | host-refute-14253-903 | started | worker-3 | 14253 [tool.pytest] int on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:48 JST | host-refute-14447-903 | completed | worker-1 | 14447 9.0.3 rc=1 3 failed; HOLD no View |
| 2026-09-09 19:04:48 JST | host-refute-14095-903 | completed | worker-2 | 14095 9.0.3 rc=1 0==1; HOLD no View |
| 2026-09-09 19:04:48 JST | host-refute-14253-903 | completed | worker-3 | 14253 9.0.3 [tool.pytest] TypeError rc=3; HOLD no View |
| 2026-09-09 19:04:48 JST | host-refute-14092-903 | started | worker-1 | 14092 int retention on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:48 JST | host-refute-14094-903 | started | worker-2 | 14094 Monkeypatch on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:04:48 JST | host-refute-14650-903 | started | worker-3 | 14650 strict ids on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:04 JST | host-refute-14092-903 | completed | worker-1 | 14092 9.0.3 TypeError rc=3; HOLD no View |
| 2026-09-09 19:05:04 JST | host-refute-14094-903 | completed | worker-2 | 14094 9.0.3 Monkeypatch AttributeError; HOLD no View |
| 2026-09-09 19:05:04 JST | host-refute-14650-903 | completed | worker-3 | 14650 9.0.3 duplicate IDs rc=2; HOLD no View |
| 2026-09-09 19:05:04 JST | host-refute-14514-903 | started | worker-1 | 14514 foo.test.py collect on 9.0.3; HOLD feature; not Dreamer |
| 2026-09-09 19:05:04 JST | host-refute-13882-903 | started | worker-2 | 13882 subclass fixtures on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:04 JST | host-refute-14004-903 | started | worker-3 | 14004 nested autouse on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:19 JST | host-refute-14514-903 | completed | worker-1 | 14514 9.0.3 collect foo.test ImportError; HOLD feature |
| 2026-09-09 19:05:19 JST | host-refute-13882-903 | completed | worker-2 | 13882 9.0.3 2 pass; HOLD no View |
| 2026-09-09 19:05:19 JST | host-refute-14004-903 | completed | worker-3 | 14004 9.0.3 4 pass; HOLD no View |
| 2026-09-09 19:05:19 JST | host-refute-14431-903 | started | worker-1 | 14431 explicit test.py on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:19 JST | host-refute-13754-903 | started | worker-2 | 13754 explicit test.py on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:19 JST | host-refute-13965-903 | started | worker-3 | 13965 N=1 explicit on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:34 JST | host-reconstitute-14808 | completed | worker-1 | 14808 ini_options getini returns list; [tool.pytest] TypeError; pytest.ini pass; HOLD no View |
| 2026-09-09 19:05:34 JST | host-reconstitute-14560 | completed | worker-2 | 14560 dict-wrapper collect KeyError __name__ 8.4.1/9.0.1/9.1.1; HOLD no View |
| 2026-09-09 19:05:34 JST | hold-14613-feature | completed | worker-3 | 14613 PYTEST_CACHE_DIR_BASE feature request; HOLD no mini; not Dreamer |
| 2026-09-09 19:05:51 JST | host-refute-14431-903 | completed | worker-1 | 14431 9.0.3 explicit 1 pass; HOLD not a cache bug |
| 2026-09-09 19:05:51 JST | host-refute-13754-903 | completed | worker-2 | 13754 9.0.3 explicit 4 pass; HOLD no View |
| 2026-09-09 19:05:51 JST | host-refute-13965-903 | completed | worker-3 | 13965 9.0.3 N=1 pass; HOLD no View |
| 2026-09-09 19:05:51 JST | host-refute-14148-903 | started | worker-1 | 14148 cache on/off on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:51 JST | host-refute-14640-case2-903 | started | worker-2 | 14640 CASE2 sorted on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:05:51 JST | host-refute-14935-903 | started | worker-3 | 14935 9.0.3 two-project layout; HOLD; not Dreamer |
| 2026-09-09 19:06:15 JST | host-refute-14148-903 | completed | worker-1 | 14148 9.0.3 cache on pass / off AttributeError; HOLD no View |
| 2026-09-09 19:06:15 JST | host-refute-14640-case2-903 | completed | worker-2 | 14640 CASE2 9.0.3 3 pass; HOLD no View |
| 2026-09-09 19:06:15 JST | host-refute-14935-903 | completed | worker-3 | 14935 9.0.3 user-scoped eviction; HOLD design no View |
| 2026-09-09 19:06:15 JST | host-refute-13479-903 | started | worker-1 | 13479 freezegun on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:06:15 JST | contamination-1906 | started | worker-2 | contamination 0; FIRST_SELECTION does not relax |
| 2026-09-09 19:06:15 JST | no-resume-1906 | started | worker-3 | no expand/other resume; no Dream 0004; tree-only HOLD |
| 2026-09-09 19:06:37 JST | host-refute-13479-903 | completed | worker-1 | 13479 9.0.3+freezegun fixture ff not found; HOLD no View |
| 2026-09-09 19:06:37 JST | contamination-1906 | completed | worker-2 | contamination clean; FIRST_SELECTION does not relax |
| 2026-09-09 19:06:37 JST | no-resume-1906 | completed | worker-3 | no collect resume; no Dream 0004; no worktrees |
| 2026-09-09 19:06:37 JST | host-refute-2043-903 | started | worker-1 | 2043 indirect override on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:06:37 JST | host-refute-5203-903 | started | worker-2 | 5203 fixture override on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:06:37 JST | host-refute-13784-903 | started | worker-3 | 13784 capteesys -s on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:07:06 JST | host-refute-2043-903 | completed | worker-1 | 2043 9.0.3 4 pass; HOLD no View |
| 2026-09-09 19:07:06 JST | host-refute-5203-903 | completed | worker-2 | 5203 9.0.3 rc=1 8==6; HOLD no View |
| 2026-09-09 19:07:06 JST | host-refute-13784-903 | completed | worker-3 | 13784 9.0.3 capteesys -s stdout doubled (2); HOLD no View |
| 2026-09-09 19:07:06 JST | host-refute-13784-901s | started | worker-1 | 13784 capteesys -s on 9.0.1; HOLD; not Dreamer |
| 2026-09-09 19:07:06 JST | host-refute-13784-910s | started | worker-2 | 13784 capteesys -s on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:07:06 JST | throughput-audit-1907 | started | worker-3 | append audit; scheduler 19:14; not isomorphic R1 |
| 2026-09-09 19:07:30 JST | host-refute-13784-901s | completed | worker-1 | 13784 9.0.1 -s stdout doubled; HOLD no View |
| 2026-09-09 19:07:30 JST | host-refute-13784-910s | completed | worker-2 | 13784 9.1.0 -s stdout once; HOLD no View |
| 2026-09-09 19:07:30 JST | throughput-audit-1907 | completed | worker-3 | 13784 doubling ends at 9.1.0; not isomorphic R1 |
| 2026-09-09 19:07:30 JST | snippet-pending-1907 | started | worker-1 | tree-only 14683/14436/14635/14841 remain HOLD; not isomorphic R1 |
| 2026-09-09 19:07:30 JST | clock-gate-1907 | started | worker-2 | operate/work; hard_end not extended; no Dream 0004 |
| 2026-09-09 19:07:30 JST | jobs-rewrite-1907 | started | worker-3 | THROUGHPUT rewrite; idle_gaps 0; scheduler 19:14 |
| 2026-09-09 19:07:30 JST | snippet-pending-1907 | completed | worker-1 | tree-only remain HOLD; no PASS minted |
| 2026-09-09 19:07:30 JST | clock-gate-1907 | completed | worker-2 | operate/work; 保全 08:00 not due |
| 2026-09-09 19:07:30 JST | jobs-rewrite-1907 | completed | worker-3 | THROUGHPUT rewritten jobs=498 idle_gaps=0 |
| 2026-09-09 19:07:46 JST | host-refute-14447-plain903 | started | worker-1 | 14447 9.0.3 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:07:46 JST | host-refute-14445-plain903 | started | worker-2 | 14445 9.0.3 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:07:46 JST | host-refute-14819-plain903 | started | worker-3 | 14819 9.0.3 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:00 JST | host-refute-14447-plain903 | completed | worker-1 | 14447 9.0.3 --assert=plain 3 pass; HOLD no View |
| 2026-09-09 19:08:00 JST | host-refute-14445-plain903 | completed | worker-2 | 14445 9.0.3 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:08:00 JST | host-refute-14819-plain903 | completed | worker-3 | 14819 9.0.3 plain AssertionError short-circuit; HOLD no View |
| 2026-09-09 19:08:00 JST | host-refute-14820-plain903 | started | worker-1 | 14820 9.0.3 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:00 JST | host-refute-14447-plain910 | started | worker-2 | 14447 9.1.0 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:00 JST | host-refute-14819-plain910 | started | worker-3 | 14819 9.1.0 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:20 JST | host-refute-14820-plain903 | completed | worker-1 | 14820 9.0.3 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:08:20 JST | host-refute-14447-plain910 | completed | worker-2 | 14447 9.1.0 --assert=plain 3 pass; HOLD no View |
| 2026-09-09 19:08:20 JST | host-refute-14819-plain910 | completed | worker-3 | 14819 9.1.0 plain AssertionError short-circuit; HOLD no View |
| 2026-09-09 19:08:20 JST | host-refute-14445-plain910 | started | worker-1 | 14445 9.1.0 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:20 JST | host-refute-14820-plain910 | started | worker-2 | 14820 9.1.0 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:20 JST | host-refute-14445-plain841 | started | worker-3 | 14445 8.4.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:38 JST | host-refute-14445-plain910 | completed | worker-1 | 14445 9.1.0 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:08:38 JST | host-refute-14820-plain910 | completed | worker-2 | 14820 9.1.0 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:08:38 JST | host-refute-14445-plain841 | completed | worker-3 | 14445 8.4.1 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:08:38 JST | host-refute-14819-plain841 | started | worker-1 | 14819 8.4.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:38 JST | host-refute-14820-plain841 | started | worker-2 | 14820 8.4.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:08:38 JST | host-refute-14447-plain901 | started | worker-3 | 14447 9.0.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:09:11 JST | host-refute-14819-plain841 | completed | worker-1 | 14819 8.4.1 plain AssertionError short-circuit; HOLD no View |
| 2026-09-09 19:09:11 JST | host-refute-14820-plain841 | completed | worker-2 | 14820 8.4.1 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:09:11 JST | host-refute-14447-plain901 | completed | worker-3 | 14447 9.0.1 --assert=plain 3 pass; HOLD no View |
| 2026-09-09 19:09:11 JST | host-refute-14445-plain901 | started | worker-1 | 14445 9.0.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:09:11 JST | host-refute-14819-plain901 | started | worker-2 | 14819 9.0.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:09:11 JST | host-refute-14820-plain901 | started | worker-3 | 14820 9.0.1 --assert=plain; HOLD; not Dreamer |
| 2026-09-09 19:09:31 JST | host-refute-14445-plain901 | completed | worker-1 | 14445 9.0.1 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:09:31 JST | host-refute-14819-plain901 | completed | worker-2 | 14819 9.0.1 plain AssertionError; HOLD no View |
| 2026-09-09 19:09:31 JST | host-refute-14820-plain901 | completed | worker-3 | 14820 9.0.1 --assert=plain 2 pass; HOLD no View |
| 2026-09-09 19:09:31 JST | host-refute-14964-c2-903 | started | worker-1 | 14964 CASE2 on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:09:31 JST | host-refute-14964-c3-910 | started | worker-2 | 14964 CASE3 on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:09:31 JST | host-refute-14514-910 | started | worker-3 | 14514 collect foo.test on 9.1.0; HOLD feature; not Dreamer |
| 2026-09-09 19:09:50 JST | host-refute-14964-c2-903 | completed | worker-1 | 14964 CASE2 9.0.3 both tests ERROR guard; HOLD no View |
| 2026-09-09 19:09:50 JST | host-refute-14964-c3-910 | completed | worker-2 | 14964 CASE3 9.1.0 both tests ERROR; HOLD no View |
| 2026-09-09 19:09:50 JST | host-refute-14514-910 | completed | worker-3 | 14514 9.1.0 collect foo.test ImportError; HOLD feature |
| 2026-09-09 19:09:50 JST | contamination-1910 | started | worker-1 | contamination 0; FIRST_SELECTION does not relax |
| 2026-09-09 19:09:50 JST | clock-gate-1910 | started | worker-2 | operate/work; no Dream 0004; no collect resume |
| 2026-09-09 19:09:50 JST | hold-14841-refresh | started | worker-3 | 14841 multiprocessing+pytester remains HOLD; not reconstituted |
| 2026-09-09 19:09:51 JST | contamination-1910 | completed | worker-1 | contamination clean |
| 2026-09-09 19:09:51 JST | clock-gate-1910 | completed | worker-2 | operate/work; hard_end 09:00 not extended |
| 2026-09-09 19:09:51 JST | hold-14841-refresh | completed | worker-3 | 14841 HOLD no View; tree-only leftovers unchanged |
| 2026-09-09 19:10:09 JST | host-refute-14971-910 | started | worker-1 | 14971 interleaved nested fixture on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:10:09 JST | host-refute-14048-903 | started | worker-2 | 14048 --pyargs missing init on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:10:09 JST | host-refute-14048-910 | started | worker-3 | 14048 --pyargs missing init on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:10:36 JST | host-refute-14971-910 | completed | worker-1 | 14971 9.1.0 interleaved nested_fixture missing; HOLD no View |
| 2026-09-09 19:10:36 JST | host-refute-14048-903 | completed | worker-2 | 14048 9.0.3 --pyargs with tests/__init__.py 1 pass; HOLD no View |
| 2026-09-09 19:10:36 JST | host-refute-14048-910 | completed | worker-3 | 14048 9.1.0 --pyargs with tests/__init__.py 1 pass; HOLD no View |
| 2026-09-09 19:10:36 JST | jobs-rewrite-1910 | started | worker-1 | THROUGHPUT rewrite; idle_gaps 0 |
| 2026-09-09 19:10:36 JST | scheduler-confirm-1910 | started | worker-2 | scheduler next 19:14:29 JST; no Dream 0004 |
| 2026-09-09 19:10:36 JST | tree-hold-1910 | started | worker-3 | 14683/14436/14635/14841 remain HOLD; no extra trees |
| 2026-09-09 19:10:36 JST | jobs-rewrite-1910 | completed | worker-1 | THROUGHPUT rewritten jobs=552 idle_gaps=0 |
| 2026-09-09 19:10:36 JST | scheduler-confirm-1910 | completed | worker-2 | 01a085570c447273a54294de2d99bfcf next 19:14:29 JST |
| 2026-09-09 19:10:36 JST | tree-hold-1910 | completed | worker-3 | tree-only HOLD; no PASS |
| 2026-09-09 19:10:56 JST | host-refute-14964-c2-910 | started | worker-1 | 14964 CASE2 on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:10:56 JST | host-refute-14964-c3-903 | started | worker-2 | 14964 CASE3 on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:10:56 JST | host-refute-5203-910 | started | worker-3 | 5203 fixture override on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:11:17 JST | host-refute-14964-c2-910 | completed | worker-1 | 14964 CASE2 9.1.0 both ERROR; HOLD no View |
| 2026-09-09 19:11:17 JST | host-refute-14964-c3-903 | completed | worker-2 | 14964 CASE3 9.0.3 both ERROR; HOLD no View |
| 2026-09-09 19:11:17 JST | host-refute-5203-910 | completed | worker-3 | 5203 9.1.0 rc=1 8==6; HOLD no View |
| 2026-09-09 19:11:17 JST | host-refute-14608-root903 | started | worker-1 | 14608 pytest --from-b A B on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:11:17 JST | host-refute-14737-mod903 | started | worker-2 | 14737 module pytestmark skip on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:11:17 JST | host-refute-14691-910-done | started | worker-3 | confirm 14691 classmethod on extra versions already HOLD |
| 2026-09-09 19:11:37 JST | host-refute-14608-root903 | completed | worker-1 | 14608 9.0.3 A B --from-b 2 pass; HOLD no View |
| 2026-09-09 19:11:37 JST | host-refute-14737-mod903 | completed | worker-2 | 14737 9.0.3 module pytestmark 1 skipped; HOLD no View |
| 2026-09-09 19:11:37 JST | host-refute-14691-910-done | completed | worker-3 | 14691 classmethod still HOLD; no PASS |
| 2026-09-09 19:11:37 JST | host-refute-14737-conf903 | started | worker-1 | 14737 conftest pytestmark on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:11:37 JST | contamination-1911 | started | worker-2 | contamination 0; no Dream 0004 |
| 2026-09-09 19:11:37 JST | handoff-1914 | started | worker-3 | next 19:14 vacancy tick; tree-only HOLD; no collect resume |
| 2026-09-09 19:11:37 JST | host-refute-14737-conf903 | completed | worker-1 | 14737 9.0.3 conftest pytestmark does not skip; HOLD no View |
| 2026-09-09 19:11:37 JST | contamination-1911 | completed | worker-2 | contamination clean |
| 2026-09-09 19:11:37 JST | handoff-1914 | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf next 19:14:29 JST; idle_gaps 0 |
| 2026-09-09 19:12:04 JST | host-refute-14737-pkg903 | started | worker-1 | 14737 9.0.3 package __init__ skip still fails; HOLD; not Dreamer |
| 2026-09-09 19:12:04 JST | no-worktrees-1912 | started | worker-2 | no worktrees in run dir; no coordinator main mix |
| 2026-09-09 19:12:04 JST | r1-gate-1912 | started | worker-3 | r1 remaining; not spent on isomorphic Dream 0004 |
| 2026-09-09 19:12:04 JST | host-refute-14737-pkg903 | completed | worker-1 | 14737 9.0.3 package skip does not apply; HOLD no View |
| 2026-09-09 19:12:04 JST | no-worktrees-1912 | completed | worker-2 | no worktrees in run dir |
| 2026-09-09 19:12:04 JST | r1-gate-1912 | completed | worker-3 | r1 remaining $16.0671; no isomorphic Dream 0004 |
| 2026-09-09 19:12:22 JST | pre-1914-tick | started | worker-1 | workers free for 19:14 vacancy tick; no Dream 0004; no collect resume |
| 2026-09-09 19:12:22 JST | tree-hold-1912 | started | worker-2 | 14683/14436/14635/14841 HOLD without extra trees |
| 2026-09-09 19:12:22 JST | status-refresh-1912 | started | worker-3 | consumer still 1 discovery 小規模試行; KEEP 0 |
| 2026-09-09 19:12:22 JST | pre-1914-tick | completed | worker-1 | scheduler 01a085570c447273a54294de2d99bfcf next 19:14:29 JST |
| 2026-09-09 19:12:22 JST | tree-hold-1912 | completed | worker-2 | tree-only HOLD; no PASS |
| 2026-09-09 19:12:22 JST | status-refresh-1912 | completed | worker-3 | 小規模試行 1 discovery; HOLD not rewritten to PASS |
| 2026-09-09 19:12:33 JST | gate-tick-1912 | started | worker-1 | clock operate/work; 保全 not due |
| 2026-09-09 19:12:33 JST | no-dream-1912 | started | worker-2 | THIN_WRAPPER; no isomorphic Dream 0004 |
| 2026-09-09 19:12:33 JST | no-collect-1912 | started | worker-3 | expand/other NO_RUNNABLE_JOB; do not resume |
| 2026-09-09 19:12:34 JST | gate-tick-1912 | completed | worker-1 | operate/work |
| 2026-09-09 19:12:34 JST | no-dream-1912 | completed | worker-2 | no isomorphic R1 |
| 2026-09-09 19:12:34 JST | no-collect-1912 | completed | worker-3 | no expand/other resume |
| 2026-09-09 19:15:34 JST | host-refute-14808-matrix | started | worker-1 | 14808 getini string/array 8.4.1/9.0.3/9.1.0; HOLD no View; not Dreamer |
| 2026-09-09 19:15:34 JST | host-refute-14560-matrix | started | worker-2 | 14560 dict-wrapper parametrize 9.0.3/9.1.0; HOLD no View; not Dreamer |
| 2026-09-09 19:15:34 JST | host-reconstitute-14613 | started | worker-3 | 14613 PYTEST_ADDOPTS cache_dir per-PWD workaround; HOLD feature; not Dreamer |
| 2026-09-09 19:16:10 JST | host-refute-14808-matrix | completed | worker-1 | 14808 ini_options list no TypeError all vers; [tool.pytest] TypeError from 9.0.1; 8.4.1 unread pass; HOLD no View |
| 2026-09-09 19:16:10 JST | host-refute-14560-matrix | completed | worker-2 | 14560 KeyError __name__ collect 8.4.1-9.1.1 plus 9.0.3/9.1.0; HOLD no View |
| 2026-09-09 19:16:10 JST | host-reconstitute-14613 | completed | worker-3 | 14613 -o cache_dir unknown on 9.1.1; HOLD feature; --cache-dir queued |
| 2026-09-09 19:16:10 JST | host-refute-14613-cachedir | started | worker-1 | 14613 --cache-dir per-project dirs; HOLD feature; not Dreamer |
| 2026-09-09 19:16:10 JST | hold-9298-note | started | worker-2 | 9298 Windows pycache_prefix CI; HOLD no portable mini; not Dreamer |
| 2026-09-09 19:16:10 JST | hold-14613-note | started | worker-3 | 14613 feature PYTEST_CACHE_DIR_BASE; HOLD no View |
| 2026-09-09 19:16:13 JST | host-reconstitute-14683-mini | started | worker-1 | 14683 doctest_namespace mini without nimbus; HOLD; not Dreamer |
| 2026-09-09 19:16:13 JST | host-reconstitute-13957-ids | started | worker-2 | 13957 parametrize nodeid order collect-only; HOLD; not Dreamer |
| 2026-09-09 19:17:17 JST | host-refute-14613-cachedir | completed | worker-1 | 14613 -o cache_dir with cacheprovider writes per-project trees; env missing; HOLD feature |
| 2026-09-09 19:17:17 JST | hold-9298-note | completed | worker-2 | 9298 Windows CI HOLD; no portable mini |
| 2026-09-09 19:17:17 JST | hold-14613-note | completed | worker-3 | 14613 HOLD feature; no View |
| 2026-09-09 19:17:17 JST | docs-1914-tick | started | worker-1 | README/heartbeat/STATUS/PILOT 14808/14560/14613 HOLD not PASS |
| 2026-09-09 19:17:17 JST | contamination-1916 | started | worker-2 | contamination 0; FIRST_SELECTION does not relax |
| 2026-09-09 19:17:17 JST | no-dream-collect-1916 | started | worker-3 | no Dream 0004; no expand/other resume; tree-only HOLD |
| 2026-09-09 19:17:37 JST | host-reconstitute-14683-mini | completed | worker-1 | 14683 stripped doctest_namespace 8.4.1/9.0.1/9.1.1 pass; nimbus tree still required; HOLD no View |
| 2026-09-09 19:17:37 JST | host-reconstitute-13957-ids | completed | worker-2 | 13957 collect IDs [cpu-half-ip-1-1-True] all versions; no 8/9 swap; HOLD no View |
| 2026-09-09 19:18:00 JST | docs-1914-tick | completed | worker-1 | docs refreshed; 14808/14560/14613 HOLD not PASS |
| 2026-09-09 19:18:00 JST | contamination-1916 | completed | worker-2 | contamination clean |
| 2026-09-09 19:18:00 JST | no-dream-collect-1916 | completed | worker-3 | no Dream 0004; no collect resume; tree-only HOLD |
| 2026-09-09 19:18:00 JST | host-refute-14613-841 | started | worker-1 | 14613 -o cache_dir on 8.4.1; HOLD feature; not Dreamer |
| 2026-09-09 19:18:00 JST | hold-14762-note | started | worker-2 | 14762 3.15b4 SEGFAULT HOLD no mini; not Dreamer |
| 2026-09-09 19:18:00 JST | throughput-audit-1917 | started | worker-3 | append audit; scheduler 19:29; not isomorphic R1 |
| 2026-09-09 19:18:31 JST | host-refute-14613-841 | completed | worker-1 | 14613 8.4.1 -o cache_dir writes CACHEDIR.TAG; HOLD feature |
| 2026-09-09 19:18:31 JST | hold-14762-note | completed | worker-2 | 14762 3.15b4 SEGFAULT HOLD no mini |
| 2026-09-09 19:18:31 JST | throughput-audit-1917 | completed | worker-3 | audit appended; not isomorphic R1 |
| 2026-09-09 19:18:31 JST | host-refute-14683-matrix | started | worker-1 | 14683 stripped doctest 9.0.3/9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:18:31 JST | host-refute-13957-matrix | started | worker-2 | 13957 collect IDs 9.0.3/9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:18:31 JST | snippet-pending-1918 | started | worker-3 | 14683 stripped mini HOLD; tree-only 14436/14635/14841 remain |
| 2026-09-09 19:18:52 JST | host-refute-14683-matrix | completed | worker-1 | 14683 9.0.3/9.1.0 1 pass stripped doctest; HOLD no View |
| 2026-09-09 19:18:52 JST | host-refute-13957-matrix | completed | worker-2 | 13957 9.0.3/9.1.0 same cpu-half-ip id; HOLD no View |
| 2026-09-09 19:18:52 JST | snippet-pending-1918 | completed | worker-3 | 14683 stripped HOLD; 14436/14635/14841 tree-only HOLD |
| 2026-09-09 19:18:52 JST | hold-14436-refresh | started | worker-1 | 14436 Tavern/HA tree HOLD no reconstitution; not Dreamer |
| 2026-09-09 19:18:52 JST | hold-14635-refresh | started | worker-2 | 14635 Home Assistant tree HOLD no reconstitution; not Dreamer |
| 2026-09-09 19:18:52 JST | contamination-1918 | started | worker-3 | contamination 0; no Dream 0004; no collect resume |
| 2026-09-09 19:19:11 JST | hold-14436-refresh | completed | worker-1 | 14436 HOLD no extra tree |
| 2026-09-09 19:19:11 JST | hold-14635-refresh | completed | worker-2 | 14635 HOLD no extra tree |
| 2026-09-09 19:19:11 JST | contamination-1918 | completed | worker-3 | contamination clean; no Dream 0004 |
| 2026-09-09 19:19:11 JST | gap-screen-complete | started | worker-1 | diff complete pytest roots vs host-verify; HOLD remaining; not Dreamer |
| 2026-09-09 19:19:11 JST | clock-gate-1919 | started | worker-2 | operate/work; no collect resume |
| 2026-09-09 19:19:11 JST | jobs-rewrite-1919 | started | worker-3 | THROUGHPUT rewrite; idle_gaps 0 |
| 2026-09-09 19:20:09 JST | gap-screen-complete | completed | worker-1 | 21 leftover issues without host-verify; PRs HOLD; 14051/14476 queued |
| 2026-09-09 19:20:09 JST | clock-gate-1919 | completed | worker-2 | operate/work |
| 2026-09-09 19:20:09 JST | jobs-rewrite-1919 | completed | worker-3 | THROUGHPUT rewritten jobs=634 idle_gaps=0 |
| 2026-09-09 19:20:09 JST | host-reconstitute-14051 | started | worker-1 | 14051 pytest.main custom-arg space vs equals; HOLD; not Dreamer |
| 2026-09-09 19:20:09 JST | host-reconstitute-14476 | started | worker-2 | 14476 -k expression collect; HOLD; not Dreamer |
| 2026-09-09 19:20:09 JST | hold-13985-note | started | worker-3 | 13985 SchemaStore [tool.pytest] HOLD docs; not Dreamer |
| 2026-09-09 19:23:56 JST | host-reconstitute-14051 | completed | worker-1 | 14051 space and equals both pass 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 19:23:56 JST | host-reconstitute-14476 | completed | worker-2 | 14476 -k baidu and not logo collects search only; HOLD no View |
| 2026-09-09 19:23:56 JST | hold-13985-note | completed | worker-3 | 13985 SchemaStore HOLD docs |
| 2026-09-09 19:23:56 JST | hold-13699-note | started | worker-1 | 13699 asynctest pytest suite HOLD; not a mini; not Dreamer |
| 2026-09-09 19:23:56 JST | hold-14700-note | started | worker-2 | 14700 jaraco.test reports.py HOLD; no mini; not Dreamer |
| 2026-09-09 19:23:56 JST | docs-1920 | started | worker-3 | README/heartbeat 14051/14476 HOLD not PASS |
| 2026-09-09 19:24:24 JST | hold-13699-note | completed | worker-1 | 13699 asynctest HOLD no mini |
| 2026-09-09 19:24:25 JST | hold-14700-note | completed | worker-2 | 14700 jaraco.test HOLD no mini |
| 2026-09-09 19:24:25 JST | docs-1920 | completed | worker-3 | README/heartbeat 14051/14476 HOLD |
| 2026-09-09 19:24:25 JST | hold-14444-note | started | worker-1 | 14444 capture=sys hook HOLD feature; not Dreamer |
| 2026-09-09 19:24:25 JST | hold-13913-note | started | worker-2 | 13913 sqlalchemy conftest HOLD clone tree; not Dreamer |
| 2026-09-09 19:24:25 JST | contamination-1924 | started | worker-3 | contamination 0; no Dream 0004; no collect resume |
| 2026-09-09 19:24:40 JST | hold-14444-note | completed | worker-1 | 14444 HOLD feature no mini |
| 2026-09-09 19:24:40 JST | hold-13913-note | completed | worker-2 | 13913 HOLD sqlalchemy clone |
| 2026-09-09 19:24:40 JST | contamination-1924 | completed | worker-3 | contamination clean |
| 2026-09-09 19:24:40 JST | clock-gate-1924 | started | worker-1 | operate/work; 保全 not due |
| 2026-09-09 19:24:40 JST | r1-gate-1924 | started | worker-2 | r1 remaining; no isomorphic Dream 0004 |
| 2026-09-09 19:24:40 JST | jobs-rewrite-1924 | started | worker-3 | THROUGHPUT rewrite; idle_gaps 0; scheduler 19:29 |
| 2026-09-09 19:24:40 JST | clock-gate-1924 | completed | worker-1 | operate/work; hard_end 09:00 not extended |
| 2026-09-09 19:24:40 JST | r1-gate-1924 | completed | worker-2 | remaining $16.0671; no Dream 0004 |
| 2026-09-09 19:24:40 JST | jobs-rewrite-1924 | completed | worker-3 | THROUGHPUT rewritten jobs=658 idle_gaps=0 |
| 2026-09-09 19:24:57 JST | host-refute-14051-903 | started | worker-1 | 14051 pytest.main space/eq on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:24:57 JST | host-refute-14051-910 | started | worker-2 | 14051 pytest.main space/eq on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:24:57 JST | host-refute-14476-901 | started | worker-3 | 14476 -k on 9.0.1; HOLD; not Dreamer |
| 2026-09-09 19:25:20 JST | host-refute-14051-903 | completed | worker-1 | 14051 9.0.3 space/eq both pass; HOLD no View |
| 2026-09-09 19:25:20 JST | host-refute-14051-910 | completed | worker-2 | 14051 9.1.0 space/eq both pass; HOLD no View |
| 2026-09-09 19:25:20 JST | host-refute-14476-901 | completed | worker-3 | 14476 9.0.1 -k selects search only; HOLD no View |
| 2026-09-09 19:25:20 JST | contamination-1925 | started | worker-1 | contamination 0; FIRST_SELECTION does not relax |
| 2026-09-09 19:25:20 JST | no-worktrees-1925 | started | worker-2 | no worktrees in run dir; no coordinator main mix |
| 2026-09-09 19:25:20 JST | handoff-1929 | started | worker-3 | next 19:29 vacancy tick; no Dream 0004; no HOLD→PASS; no collect resume |
| 2026-09-09 19:25:21 JST | contamination-1925 | completed | worker-1 | contamination clean |
| 2026-09-09 19:25:21 JST | no-worktrees-1925 | completed | worker-2 | no worktrees in run dir |
| 2026-09-09 19:25:21 JST | handoff-1929 | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf next 19:29:29 JST; idle_gaps 0 |
| 2026-09-09 19:25:42 JST | host-refute-14476-910 | started | worker-1 | 14476 -k on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:25:42 JST | host-refute-14613-903 | started | worker-2 | 14613 -o cache_dir on 9.0.3; HOLD feature; not Dreamer |
| 2026-09-09 19:25:42 JST | host-refute-14613-910 | started | worker-3 | 14613 -o cache_dir on 9.1.0; HOLD feature; not Dreamer |
| 2026-09-09 19:26:04 JST | host-refute-14476-910 | completed | worker-1 | 14476 9.1.0 -k selects search only; HOLD no View |
| 2026-09-09 19:26:04 JST | host-refute-14613-903 | completed | worker-2 | 14613 9.0.3 -o cache_dir rc=0; HOLD feature |
| 2026-09-09 19:26:04 JST | host-refute-14613-910 | completed | worker-3 | 14613 9.1.0 -o cache_dir rc=0; HOLD feature |
| 2026-09-09 19:26:04 JST | clock-gate-1926 | started | worker-1 | operate/work; 保全 not due |
| 2026-09-09 19:26:04 JST | tree-hold-1926 | started | worker-2 | 14436/14635/14841 remain HOLD; no extra trees |
| 2026-09-09 19:26:04 JST | pre-1929-tick | started | worker-3 | workers for 19:29 tick; no Dream 0004; no HOLD→PASS |
| 2026-09-09 19:26:05 JST | clock-gate-1926 | completed | worker-1 | operate/work; hard_end not extended |
| 2026-09-09 19:26:05 JST | tree-hold-1926 | completed | worker-2 | tree-only HOLD |
| 2026-09-09 19:26:05 JST | pre-1929-tick | completed | worker-3 | scheduler 01a085570c447273a54294de2d99bfcf next 19:29:29 JST |
| 2026-09-09 19:26:17 JST | contamination-1926 | started | worker-1 | contamination 0; FIRST_SELECTION does not relax |
| 2026-09-09 19:26:17 JST | r1-gate-1926 | started | worker-2 | r1 remaining $16.0671; no isomorphic Dream 0004 |
| 2026-09-09 19:26:17 JST | no-collect-1926 | started | worker-3 | expand/other NO_RUNNABLE_JOB; do not resume |
| 2026-09-09 19:26:17 JST | contamination-1926 | completed | worker-1 | contamination clean |
| 2026-09-09 19:26:17 JST | r1-gate-1926 | completed | worker-2 | no Dream 0004 |
| 2026-09-09 19:26:17 JST | no-collect-1926 | completed | worker-3 | no expand/other resume |
| 2026-09-09 19:26:27 JST | status-1927 | started | worker-1 | consumer 1 discovery 小規模試行; KEEP 0 |
| 2026-09-09 19:26:27 JST | scheduler-confirm-1927 | started | worker-2 | 01a085570c447273a54294de2d99bfcf next 19:29:29 JST |
| 2026-09-09 19:26:27 JST | no-pass-1927 | started | worker-3 | HOLD not rewritten to PASS; reviewer_type agent |
| 2026-09-09 19:26:27 JST | status-1927 | completed | worker-1 | 小規模試行 1 discovery; 32113 not 未知holdout |
| 2026-09-09 19:26:27 JST | scheduler-confirm-1927 | completed | worker-2 | scheduler armed 15m |
| 2026-09-09 19:26:27 JST | no-pass-1927 | completed | worker-3 | HOLD stays HOLD |
| 2026-09-09 19:26:39 JST | gate-tick-1927 | started | worker-1 | operate/work deadline clocks |
| 2026-09-09 19:26:39 JST | no-dream-1927 | started | worker-2 | THIN_WRAPPER; no isomorphic Dream 0004 |
| 2026-09-09 19:26:39 JST | snippet-pending-1927 | started | worker-3 | 14436/14635/14841 tree-only HOLD |
| 2026-09-09 19:26:39 JST | gate-tick-1927 | completed | worker-1 | operate/work |
| 2026-09-09 19:26:39 JST | no-dream-1927 | completed | worker-2 | no isomorphic R1 |
| 2026-09-09 19:26:39 JST | snippet-pending-1927 | completed | worker-3 | tree-only HOLD no extra trees |
| 2026-09-09 19:26:52 JST | jobs-rewrite-1927 | started | worker-1 | THROUGHPUT rewrite |
| 2026-09-09 19:26:52 JST | no-main-mix-1927 | started | worker-2 | coordinator main not mixed |
| 2026-09-09 19:26:52 JST | keep0-1927 | started | worker-3 | FIRST_SELECTION KEEP 0; extras HOLD |
| 2026-09-09 19:26:52 JST | jobs-rewrite-1927 | completed | worker-1 | THROUGHPUT rewritten jobs=706 idle_gaps=0 |
| 2026-09-09 19:26:52 JST | no-main-mix-1927 | completed | worker-2 | no candidate merge onto main |
| 2026-09-09 19:26:52 JST | keep0-1927 | completed | worker-3 | KEEP 0; HOLD extras |
| 2026-09-09 19:27:05 JST | hdd-status-1927 | started | worker-1 | hdd.py status case-001-a; no re-init |
| 2026-09-09 19:27:05 JST | no-pass-1928 | started | worker-2 | HOLD stays HOLD |
| 2026-09-09 19:27:05 JST | scheduler-armed-1928 | started | worker-3 | 15m scheduler armed |
| 2026-09-09 19:27:05 JST | hdd-status-1927 | completed | worker-1 | case-001-a iteration 3 THIN_WRAPPER; not re-inited |
| 2026-09-09 19:27:05 JST | no-pass-1928 | completed | worker-2 | HOLD not PASS |
| 2026-09-09 19:27:05 JST | scheduler-armed-1928 | completed | worker-3 | 01a085570c447273a54294de2d99bfcf next 19:29:29 JST |
| 2026-09-09 19:27:16 JST | pre-1929b | started | worker-1 | 19:29 tick should take next non-Dream job |
| 2026-09-09 19:27:16 JST | no-collect-1928 | started | worker-2 | NO_RUNNABLE_JOB; do not resume expand/other |
| 2026-09-09 19:27:16 JST | keep-hold-1928 | started | worker-3 | tree-only and extras HOLD; no PASS |
| 2026-09-09 19:27:16 JST | pre-1929b | completed | worker-1 | vacancy continues until 08:00 保全 |
| 2026-09-09 19:27:16 JST | no-collect-1928 | completed | worker-2 | no resume |
| 2026-09-09 19:27:16 JST | keep-hold-1928 | completed | worker-3 | HOLD stays HOLD |
| 2026-09-09 19:27:27 JST | worktree-1928 | started | worker-1 | no worktrees in run dir |
| 2026-09-09 19:27:27 JST | scale-1928 | started | worker-2 | 小規模試行 1 discovery |
| 2026-09-09 19:27:27 JST | reviewer-1928 | started | worker-3 | reviewer_type agent not human |
| 2026-09-09 19:27:27 JST | worktree-1928 | completed | worker-1 | no worktrees |
| 2026-09-09 19:27:27 JST | scale-1928 | completed | worker-2 | not 未知holdout |
| 2026-09-09 19:27:27 JST | reviewer-1928 | completed | worker-3 | agent reviews; not human |
| 2026-09-09 19:27:38 JST | handoff-1929c | started | worker-1 | 19:29 tick next non-Dream job |
| 2026-09-09 19:27:38 JST | no-dream-1929 | started | worker-2 | no isomorphic Dream 0004 |
| 2026-09-09 19:27:38 JST | hold-stay-1929 | started | worker-3 | HOLD not PASS |
| 2026-09-09 19:27:38 JST | handoff-1929c | completed | worker-1 | scheduler next 19:29:29 JST |
| 2026-09-09 19:27:38 JST | no-dream-1929 | completed | worker-2 | THIN_WRAPPER stopped |
| 2026-09-09 19:27:38 JST | hold-stay-1929 | completed | worker-3 | HOLD stays HOLD |
| 2026-09-09 19:30:11 JST | host-reconstitute-14444 | started | worker-1 | 14444 pytest_load_initial_conftests force capture=sys; HOLD feature; not Dreamer |
| 2026-09-09 19:30:11 JST | hold-14841-1929 | started | worker-2 | 14841 multiprocessing+pytester remains HOLD; not reconstituted; not Dreamer |
| 2026-09-09 19:30:11 JST | hold-tree-1929 | started | worker-3 | 14436/14635 HA/Tavern trees remain HOLD; no extra trees; not Dreamer |
| 2026-09-09 19:31:27 JST | host-reconstitute-14444 | completed | worker-1 | 14444 load_initial_conftests append --capture=sys still fd; HOLD feature no View |
| 2026-09-09 19:31:27 JST | hold-14841-1929 | completed | worker-2 | 14841 remains HOLD; not reconstituted |
| 2026-09-09 19:31:27 JST | hold-tree-1929 | completed | worker-3 | 14436/14635 remain HOLD without extra trees |
| 2026-09-09 19:31:27 JST | host-refute-14444-configure | started | worker-1 | 14444 pytest_configure option.capture=sys; HOLD; not Dreamer |
| 2026-09-09 19:31:27 JST | hold-14444-note | started | worker-2 | 14444 feature HOLD; tractor tree not cloned |
| 2026-09-09 19:31:27 JST | throughput-audit-1931 | started | worker-3 | append audit; scheduler next 19:44; not isomorphic R1 |
| 2026-09-09 19:31:31 JST | host-reconstitute-14436-mini | started | worker-1 | 14436 caplog.at_level without logging plugin / session fixture; HOLD; not Dreamer |
| 2026-09-09 19:31:31 JST | host-reconstitute-13699-asynctest | started | worker-2 | 13699 asynctest import on py3.14; HOLD; not Dreamer |
| 2026-09-09 19:32:10 JST | host-refute-14444-configure | completed | worker-1 | 14444 pytest_configure can set capture=sys; load_initial_conftests cannot; HOLD feature |
| 2026-09-09 19:32:10 JST | hold-14444-note | completed | worker-2 | 14444 HOLD feature; tractor not cloned |
| 2026-09-09 19:32:10 JST | throughput-audit-1931 | completed | worker-3 | 14444 recorded; scheduler 19:44; not isomorphic R1 |
| 2026-09-09 19:32:10 JST | host-reconstitute-14392 | started | worker-1 | 14392 is_fully_escaped consecutive backslashes; HOLD; not Dreamer |
| 2026-09-09 19:32:10 JST | docs-1929-tick | started | worker-2 | README/heartbeat 14444 HOLD not PASS |
| 2026-09-09 19:32:10 JST | contamination-1931 | started | worker-3 | contamination 0; no Dream 0004; no collect resume |
| 2026-09-09 19:32:54 JST | host-reconstitute-14436-mini | completed | worker-1 | 14436 happy caplog pass; session ScopeMismatch; no:logging fixture missing; tavern KeyError not reproduced; HOLD no View |
| 2026-09-09 19:32:54 JST | host-reconstitute-13699-asynctest | completed | worker-2 | 13699 asynctest 0.13.0 on 3.14 asyncio.coroutine AttributeError; importorskip does not skip; HOLD no View |
| 2026-09-09 19:33:10 JST | host-reconstitute-14392 | completed | worker-1 | 14392 is_fully_escaped True 8.4.1/9.0.1 False 9.1.1; HOLD no View |
| 2026-09-09 19:33:10 JST | docs-1929-tick | completed | worker-2 | 14444/14392 HOLD recorded |
| 2026-09-09 19:33:10 JST | contamination-1931 | completed | worker-3 | contamination clean; no Dream 0004 |
| 2026-09-09 19:33:10 JST | host-refute-14392-extra | started | worker-1 | 14392 is_fully_escaped on 9.0.3/9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:33:10 JST | host-refute-14444-903 | started | worker-2 | 14444 hook vs configure on 9.0.3; HOLD; not Dreamer |
| 2026-09-09 19:33:10 JST | throughput-audit-1932 | started | worker-3 | append audit; scheduler 19:44; not isomorphic R1 |
| 2026-09-09 19:34:00 JST | host-refute-14392-extra | completed | worker-1 | 14392 9.0.3 True / 9.1.0 False; HOLD no View |
| 2026-09-09 19:34:00 JST | host-refute-14444-903 | completed | worker-2 | 14444 9.0.3 hook still fd, configure sys; HOLD feature |
| 2026-09-09 19:34:00 JST | throughput-audit-1932 | completed | worker-3 | audit appended; not isomorphic R1 |
| 2026-09-09 19:34:00 JST | host-refute-14444-910 | started | worker-1 | 14444 hook vs configure on 9.1.0; HOLD; not Dreamer |
| 2026-09-09 19:34:00 JST | hold-comment-leftovers | started | worker-2 | 13755/13834/12689/13910 comment-only HOLD; not Dreamer |
| 2026-09-09 19:34:00 JST | contamination-1933 | started | worker-3 | contamination 0; no Dream 0004; no collect resume |
| 2026-09-09 19:34:20 JST | host-refute-14444-910 | completed | worker-1 | 14444 9.1.0 hook still fd, configure sys; HOLD feature |
| 2026-09-09 19:34:20 JST | hold-comment-leftovers | completed | worker-2 | 13755/13834/12689/13910 comment-only HOLD |
| 2026-09-09 19:34:20 JST | contamination-1933 | completed | worker-3 | contamination clean; no Dream 0004 |
| 2026-09-09 19:34:20 JST | clock-gate-1934 | started | worker-1 | operate/work; 保全 not due |
| 2026-09-09 19:34:20 JST | tree-hold-1934 | started | worker-2 | 14436/14635/14841 HOLD without extra trees |
| 2026-09-09 19:34:20 JST | jobs-rewrite-1934 | started | worker-3 | THROUGHPUT rewrite; idle_gaps 0; scheduler 19:44 |
| 2026-09-09 19:34:20 JST | clock-gate-1934 | completed | worker-1 | operate/work; hard_end not extended |
| 2026-09-09 19:34:20 JST | tree-hold-1934 | completed | worker-2 | tree-only HOLD |
| 2026-09-09 19:34:20 JST | jobs-rewrite-1934 | completed | worker-3 | THROUGHPUT rewritten jobs=770 idle_gaps=0 |
| 2026-09-09 19:35:04 JST | host-refute-14444-cfg841 | started | worker-1 | 14444 pytest_configure on 8.4.1; HOLD; not Dreamer |
| 2026-09-09 19:35:04 JST | r1-gate-1934 | started | worker-2 | r1 remaining; no isomorphic Dream 0004 |
| 2026-09-09 19:35:04 JST | hold-14841-1934 | started | worker-3 | 14841 remains HOLD; not reconstituted |
| 2026-09-09 19:35:55 JST | host-refute-14444-cfg841 | completed | worker-1 | 14444 8.4.1 pytest_configure sets capture=sys; HOLD feature |
| 2026-09-09 19:35:55 JST | r1-gate-1934 | completed | worker-2 | r1 remaining $16.0671; no Dream 0004 |
| 2026-09-09 19:35:55 JST | hold-14841-1934 | completed | worker-3 | 14841 HOLD no reconstitution |
| 2026-09-09 19:35:55 JST | contamination-1935 | started | worker-1 | contamination 0; FIRST_SELECTION does not relax |
| 2026-09-09 19:35:55 JST | no-collect-1935 | started | worker-2 | NO_RUNNABLE_JOB; do not resume expand/other |
| 2026-09-09 19:35:55 JST | keep0-1935 | started | worker-3 | FIRST_SELECTION KEEP 0; extras HOLD not PASS |
| 2026-09-09 19:35:55 JST | contamination-1935 | completed | worker-1 | contamination clean |
| 2026-09-09 19:35:55 JST | no-collect-1935 | completed | worker-2 | no expand/other resume |
| 2026-09-09 19:35:55 JST | keep0-1935 | completed | worker-3 | KEEP 0; HOLD extras |
| 2026-09-09 19:36:10 JST | verify-evidence-index | started | worker-1 | index verification captures in scratch; not Dreamer |
| 2026-09-09 19:36:10 JST | clock-gate-1936 | started | worker-2 | operate/work; 保全 not due |
| 2026-09-09 19:36:10 JST | tree-hold-1936 | started | worker-3 | 14436/14635/14841 HOLD; no extra trees |
| 2026-09-09 19:36:29 JST | verify-evidence-index | completed | worker-1 | scratch has gates/init/export/dream/runpair/throughput captures; 保全/HARD_STOP not due |
| 2026-09-09 19:36:29 JST | clock-gate-1936 | completed | worker-2 | operate/work; hard_end not extended |
| 2026-09-09 19:36:29 JST | tree-hold-1936 | completed | worker-3 | 14436/14635/14841 HOLD no extra trees |
| 2026-09-09 19:36:29 JST | r1-gate-1936 | started | worker-1 | r1 remaining $16.0671; no Dream 0004 |
| 2026-09-09 19:36:29 JST | no-collect-1936 | started | worker-2 | NO_RUNNABLE_JOB; do not resume |
| 2026-09-09 19:36:29 JST | jobs-rewrite-1936 | started | worker-3 | THROUGHPUT rewrite; idle_gaps 0 |
| 2026-09-09 19:36:29 JST | r1-gate-1936 | completed | worker-1 | no isomorphic R1 |
| 2026-09-09 19:36:29 JST | no-collect-1936 | completed | worker-2 | no expand/other resume |
| 2026-09-09 19:36:29 JST | jobs-rewrite-1936 | completed | worker-3 | THROUGHPUT rewritten jobs=794 idle_gaps=0 |
| 2026-09-09 19:38:08 JST | hold-14084-pr | started | worker-1 | 14084 PR fixes 14048; 正解 HOLD off Dreamer |
| 2026-09-09 19:38:08 JST | hold-14210-pr | started | worker-2 | 14210 PR 正解 HOLD off Dreamer (already HOLD-14210) |
| 2026-09-09 19:38:08 JST | contamination-1936 | started | worker-3 | contamination 0; no Dream 0004 |
| 2026-09-09 19:38:08 JST | hold-14084-pr | completed | worker-1 | 14084 repair PR HOLD 正解 off Dreamer |
| 2026-09-09 19:38:08 JST | hold-14210-pr | completed | worker-2 | 14210 repair PR remains HOLD 正解 |
| 2026-09-09 19:38:08 JST | contamination-1936 | completed | worker-3 | contamination clean |
| 2026-09-09 19:38:30 JST | clock-gate-1938 | started | worker-1 | operate/work; 保全 not due |
| 2026-09-09 19:38:30 JST | tree-hold-1938 | started | worker-2 | 14436/14635/14841 HOLD no extra trees |
| 2026-09-09 19:38:30 JST | jobs-rewrite-1938 | started | worker-3 | THROUGHPUT rewrite; idle_gaps 0 |
| 2026-09-09 19:38:30 JST | clock-gate-1938 | completed | worker-1 | operate/work; hard_end not extended |
| 2026-09-09 19:38:30 JST | tree-hold-1938 | completed | worker-2 | tree-only HOLD |
| 2026-09-09 19:38:30 JST | jobs-rewrite-1938 | completed | worker-3 | THROUGHPUT rewritten jobs=806 idle_gaps=0 |
| 2026-09-09 19:38:43 JST | r1-gate-1938 | started | worker-1 | r1 remaining $16.0671; no Dream 0004 |
| 2026-09-09 19:38:43 JST | no-collect-1938 | started | worker-2 | NO_RUNNABLE_JOB; do not resume |
| 2026-09-09 19:38:43 JST | keep0-1938 | started | worker-3 | KEEP 0; HOLD extras; 小規模試行 |
| 2026-09-09 19:38:44 JST | r1-gate-1938 | completed | worker-1 | no isomorphic R1 |
| 2026-09-09 19:38:44 JST | no-collect-1938 | completed | worker-2 | no expand/other resume |
| 2026-09-09 19:38:44 JST | keep0-1938 | completed | worker-3 | KEEP 0; HOLD not PASS |
| 2026-09-09 19:38:57 JST | contamination-1939 | started | worker-1 | contamination 0; FIRST_SELECTION does not relax |
| 2026-09-09 19:38:57 JST | no-worktrees-1939 | started | worker-2 | no worktrees in run dir; no coordinator main mix |
| 2026-09-09 19:38:57 JST | scheduler-confirm-1939 | started | worker-3 | 01a085570c447273a54294de2d99bfcf next 19:44:29 JST |
| 2026-09-09 19:38:57 JST | contamination-1939 | completed | worker-1 | contamination clean |
| 2026-09-09 19:38:57 JST | no-worktrees-1939 | completed | worker-2 | no worktrees |
| 2026-09-09 19:38:57 JST | scheduler-confirm-1939 | completed | worker-3 | scheduler armed 15m |
| 2026-09-09 19:39:12 JST | hold-14104-pr | started | worker-1 | 14104 PR HOLD 正解 off Dreamer |
| 2026-09-09 19:39:12 JST | clock-gate-1939 | started | worker-2 | operate/work; 保全 not due |
| 2026-09-09 19:39:12 JST | no-dream-1939 | started | worker-3 | THIN_WRAPPER; no isomorphic Dream 0004 |
| 2026-09-09 19:39:12 JST | hold-14104-pr | completed | worker-1 | 14104 PR HOLD 正解 |
| 2026-09-09 19:39:12 JST | clock-gate-1939 | completed | worker-2 | operate/work |
| 2026-09-09 19:39:12 JST | no-dream-1939 | completed | worker-3 | no isomorphic R1 |
| 2026-09-09 19:39:25 JST | jobs-rewrite-1939 | started | worker-1 | THROUGHPUT rewrite |
| 2026-09-09 19:39:25 JST | tree-hold-1939 | started | worker-2 | 14436/14635/14841 HOLD |
| 2026-09-09 19:39:25 JST | scale-1939 | started | worker-3 | 小規模試行 1 discovery; not 未知holdout |
| 2026-09-09 19:39:25 JST | jobs-rewrite-1939 | completed | worker-1 | THROUGHPUT rewritten jobs=830 idle_gaps=0 |
| 2026-09-09 19:39:25 JST | tree-hold-1939 | completed | worker-2 | tree-only HOLD no extra trees |
| 2026-09-09 19:39:25 JST | scale-1939 | completed | worker-3 | 1 discovery 小規模試行 |
| 2026-09-09 19:39:48 JST | r1-gate-1939 | started | worker-1 | no isomorphic Dream 0004 |
| 2026-09-09 19:39:48 JST | no-collect-1939 | started | worker-2 | no expand/other resume |
| 2026-09-09 19:39:48 JST | hold-stay-1939 | started | worker-3 | HOLD not rewritten to PASS |
| 2026-09-09 19:39:48 JST | r1-gate-1939 | completed | worker-1 | remaining $16.0671 unused for filler Dream |
| 2026-09-09 19:39:48 JST | no-collect-1939 | completed | worker-2 | NO_RUNNABLE_JOB stop resume |
| 2026-09-09 19:39:48 JST | hold-stay-1939 | completed | worker-3 | reviewer_type agent; HOLD stays HOLD |
| 2026-09-09 19:40:15 JST | gate-tick-1940 | started | worker-1 | operate/work deadline clocks |
| 2026-09-09 19:40:15 JST | hdd-status-1940 | started | worker-2 | case-001-a status; no re-init |
| 2026-09-09 19:40:15 JST | pre-1944 | started | worker-3 | 19:44 tick next non-Dream job |
| 2026-09-09 19:40:15 JST | gate-tick-1940 | completed | worker-1 | operate/work |
| 2026-09-09 19:40:15 JST | hdd-status-1940 | completed | worker-2 | iteration 3 THIN_WRAPPER; not re-inited |
| 2026-09-09 19:40:15 JST | pre-1944 | completed | worker-3 | scheduler next 19:44:29 JST |
| 2026-09-09 19:40:29 JST | contamination-1940 | started | worker-1 | contamination 0 |
| 2026-09-09 19:40:29 JST | no-worktrees-1940 | started | worker-2 | no worktrees in run dir |
| 2026-09-09 19:40:29 JST | no-collect-1940 | started | worker-3 | do not resume expand/other |
| 2026-09-09 19:40:29 JST | contamination-1940 | completed | worker-1 | contamination clean |
| 2026-09-09 19:40:29 JST | no-worktrees-1940 | completed | worker-2 | no worktrees |
| 2026-09-09 19:40:29 JST | no-collect-1940 | completed | worker-3 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 19:40:42 JST | r1-gate-1940 | started | worker-1 | no isomorphic Dream 0004 |
| 2026-09-09 19:40:42 JST | keep0-1940 | started | worker-2 | KEEP 0; HOLD extras |
| 2026-09-09 19:40:42 JST | tree-hold-1940 | started | worker-3 | 14436/14635/14841 HOLD |
| 2026-09-09 19:40:42 JST | r1-gate-1940 | completed | worker-1 | remaining $16.0671 |
| 2026-09-09 19:40:42 JST | keep0-1940 | completed | worker-2 | HOLD not PASS |
| 2026-09-09 19:40:42 JST | tree-hold-1940 | completed | worker-3 | no extra trees |
| 2026-09-09 19:40:56 JST | jobs-rewrite-1941 | started | worker-1 | THROUGHPUT rewrite |
| 2026-09-09 19:40:56 JST | clock-gate-1941 | started | worker-2 | operate/work |
| 2026-09-09 19:40:56 JST | scheduler-confirm-1941 | started | worker-3 | next 19:44:29 JST |
| 2026-09-09 19:40:56 JST | jobs-rewrite-1941 | completed | worker-1 | THROUGHPUT rewritten jobs=860 idle_gaps=0 |
| 2026-09-09 19:40:56 JST | clock-gate-1941 | completed | worker-2 | operate/work; hard_end not extended |
| 2026-09-09 19:40:56 JST | scheduler-confirm-1941 | completed | worker-3 | 01a085570c447273a54294de2d99bfcf armed 15m |
| 2026-09-09 19:41:09 JST | pre-1944b | started | worker-1 | 19:44 tick takes next non-Dream job |
| 2026-09-09 19:41:09 JST | no-dream-1941 | started | worker-2 | no isomorphic Dream 0004 |
| 2026-09-09 19:41:09 JST | hold-stay-1941 | started | worker-3 | HOLD stays HOLD |
| 2026-09-09 19:41:09 JST | pre-1944b | completed | worker-1 | vacancy continues until 08:00 保全 |
| 2026-09-09 19:41:09 JST | no-dream-1941 | completed | worker-2 | THIN_WRAPPER stopped |
| 2026-09-09 19:41:09 JST | hold-stay-1941 | completed | worker-3 | no HOLD→PASS |
| 2026-09-09 19:41:21 JST | contamination-1941 | started | worker-1 | contamination 0 |
| 2026-09-09 19:41:21 JST | no-worktrees-1941 | started | worker-2 | no worktrees in run dir |
| 2026-09-09 19:41:21 JST | no-collect-1941 | started | worker-3 | no expand/other resume |
| 2026-09-09 19:41:21 JST | contamination-1941 | completed | worker-1 | contamination clean |
| 2026-09-09 19:41:21 JST | no-worktrees-1941 | completed | worker-2 | no worktrees |
| 2026-09-09 19:41:21 JST | no-collect-1941 | completed | worker-3 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 19:46:34 JST | host-reconstitute-14841 | started | worker-1 | 14841 public pytester+multiprocessing snippet; HOLD; not Dreamer |
| 2026-09-09 19:47:28 JST | host-reconstitute-14841 | completed | worker-1 | 14841 8.4.1/9.1.1 rc=1 1 failed/3 passed deferred-import-fail resource_tracker; HOLD no View |
| 2026-09-09 19:48:39 JST | clock-gate-1944 | started | coordinator | operate/work; occupy 19:44 tick |
| 2026-09-09 19:48:39 JST | scheduler-confirm-1944 | started | coordinator | 01a085570c447273a54294de2d99bfcf 15m |
| 2026-09-09 19:48:39 JST | host-reconstitute-14696 | started | worker-1 | idents.txt option-value mini; HOLD not PASS |
| 2026-09-09 19:48:39 JST | host-reconstitute-14841 | started | worker-2 | public pytester+mp snippet; HOLD not PASS |
| 2026-09-09 19:48:39 JST | host-reconstitute-14448 | started | worker-3 | rewrite subscript/ifexp messages; HOLD not PASS |
| 2026-09-09 19:53:30 JST | host-reconstitute-14696 | completed | worker-1 | idents.txt unrecognized 8.4.1-9.1.1; missing file loads except 9.1.0; HOLD no View |
| 2026-09-09 19:53:30 JST | host-reconstitute-14841 | completed | worker-2 | deferred-import-fail resource_tracker 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 19:53:30 JST | host-reconstitute-14448 | completed | worker-3 | rewrite no where-line 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 19:53:30 JST | host-reconstitute-14323 | started | worker-1 | Popen DEVNULL comment snippet; HOLD |
| 2026-09-09 19:53:30 JST | host-reconstitute-14323 | completed | worker-1 | all capture modes pass macOS 3.14; HOLD no View |
| 2026-09-09 19:53:30 JST | host-refute-13479-901 | started | worker-3 | version-matrix fill |
| 2026-09-09 19:53:30 JST | host-refute-13479-901 | completed | worker-3 | 9.0.1 ff not found; HOLD |
| 2026-09-09 19:53:30 JST | host-refute-14048-901 | completed | worker-3 | 9.0.1 noinit rc=4; with init 1 pass; HOLD |
| 2026-09-09 19:53:30 JST | host-refute-13754-910 | completed | worker-3 | 9.1.0 setup-plan rc=0 4 pass; HOLD |
| 2026-09-09 19:53:30 JST | host-refute-14148-910 | completed | worker-3 | 9.1.0 cache on pass / off AttributeError; HOLD |
| 2026-09-09 19:53:30 JST | clock-gate-1944 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 19:53:30 JST | scheduler-confirm-1944 | completed | coordinator | 01a085570c447273a54294de2d99bfcf armed 15m |
| 2026-09-09 19:53:30 JST | contamination-1944 | started | worker-1 | contamination 0 |
| 2026-09-09 19:53:30 JST | no-worktrees-1944 | started | worker-2 | no worktrees in run dir |
| 2026-09-09 19:53:30 JST | no-collect-1944 | started | worker-3 | no expand/other resume |
| 2026-09-09 19:53:30 JST | contamination-1944 | completed | worker-1 | contamination clean |
| 2026-09-09 19:53:30 JST | no-worktrees-1944 | completed | worker-2 | no worktrees |
| 2026-09-09 19:53:30 JST | no-collect-1944 | completed | worker-3 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 19:53:30 JST | keep0-1944 | started | worker-1 | KEEP 0; HOLD extras |
| 2026-09-09 19:53:30 JST | no-dream-1944 | started | worker-2 | no isomorphic Dream 0004 |
| 2026-09-09 19:53:30 JST | tree-hold-1944 | started | worker-3 | 14635 HOLD without extra trees |
| 2026-09-09 19:53:30 JST | keep0-1944 | completed | worker-1 | HOLD not PASS |
| 2026-09-09 19:53:30 JST | no-dream-1944 | completed | worker-2 | THIN_WRAPPER stopped |
| 2026-09-09 19:53:30 JST | tree-hold-1944 | completed | worker-3 | no extra trees |
| 2026-09-09 19:55:15 JST | leftover-pr-hold-1944 | started | worker-1 | 14446/14593/14622/14821/14850/14098 HOLD notes; no PASS |
| 2026-09-09 19:55:15 JST | leftover-pr-hold-1944 | completed | worker-1 | PRs stay HOLD; 正解 off Dreamer |
| 2026-09-09 19:55:15 JST | scheduler-confirm-1944b | started | worker-2 | next 19:59:29 JST |
| 2026-09-09 19:55:15 JST | scheduler-confirm-1944b | completed | worker-2 | 01a085570c447273a54294de2d99bfcf armed 15m |
| 2026-09-09 19:55:15 JST | tree-hold-14635 | started | worker-3 | 14635 HA tree HOLD no extra trees |
| 2026-09-09 19:55:15 JST | tree-hold-14635 | completed | worker-3 | no extra trees |
| 2026-09-09 19:55:15 JST | pre-1959 | started | worker-1 | 19:59 tick takes next non-Dream job |
| 2026-09-09 19:55:15 JST | no-dream-1953 | started | worker-2 | no isomorphic Dream 0004 |
| 2026-09-09 19:55:15 JST | hold-stay-1953 | started | worker-3 | HOLD stays HOLD |
| 2026-09-09 19:55:15 JST | pre-1959 | completed | worker-1 | vacancy continues until 08:00 保全 |
| 2026-09-09 19:55:15 JST | no-dream-1953 | completed | worker-2 | THIN_WRAPPER stopped |
| 2026-09-09 19:55:15 JST | hold-stay-1953 | completed | worker-3 | no HOLD→PASS; KEEP 0 |
| 2026-09-09 19:56:01 JST | host-reconstitute-14488 | started | worker-1 | caplog handler stash KeyError; HOLD not PASS |
| 2026-09-09 19:56:01 JST | host-reconstitute-14488 | completed | worker-1 | opaque KeyError 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 19:56:01 JST | contamination-1956 | started | worker-2 | contamination 0 |
| 2026-09-09 19:56:01 JST | no-collect-1956 | started | worker-3 | no expand/other resume |
| 2026-09-09 19:56:01 JST | contamination-1956 | completed | worker-2 | contamination clean |
| 2026-09-09 19:56:01 JST | no-collect-1956 | completed | worker-3 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 19:56:53 JST | host-refute-14436-extra | started | worker-2 | 14436 9.0.1/9.0.3/9.1.0 matrix; HOLD |
| 2026-09-09 19:56:53 JST | host-refute-14436-extra | completed | worker-2 | happy pass; nolog fixture missing; session ScopeMismatch; HOLD |
| 2026-09-09 19:56:53 JST | pre-1959c | started | worker-1 | 19:59 tick next non-Dream |
| 2026-09-09 19:56:53 JST | no-dream-1957 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 19:56:53 JST | pre-1959c | completed | worker-1 | vacancy continues until 08:00 保全 |
| 2026-09-09 19:56:53 JST | no-dream-1957 | completed | worker-3 | THIN_WRAPPER stopped; KEEP 0 |
| 2026-09-09 19:58:35 JST | clock-gate-1959 | started | coordinator | operate/work; occupy 19:59 tick |
| 2026-09-09 19:58:35 JST | scheduler-confirm-1959 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 19:59:29 |
| 2026-09-09 19:58:35 JST | host-reconstitute-14635-mini | started | worker-1 | HA-pattern mini without cloning core; HOLD not PASS |
| 2026-09-09 19:58:35 JST | leftover-snippet-screen-1959 | started | worker-2 | next leftover public snippets; HOLD not PASS |
| 2026-09-09 19:58:35 JST | version-matrix-1959 | started | worker-3 | fill remaining version gaps; HOLD not PASS |
| 2026-09-09 20:01:44 JST | host-reconstitute-13985 | started | worker-1 | 13985 [tool.pytest] pyproject accepted by pytest 9; HOLD schema PSA; not Dreamer |
| 2026-09-09 20:01:44 JST | leftover-hold-trees-2000 | started | worker-2 | 13913/14700/14762/9298/14877 remain HOLD without extra trees; not PASS |
| 2026-09-09 20:01:44 JST | host-reconstitute-14635-mini | completed | worker-1 | 14635 HA-pattern mini all versions collect/run pass; reporter not reproduced; HOLD no View |
| 2026-09-09 20:01:53 JST | clock-gate-1959 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:01:53 JST | scheduler-confirm-1959 | completed | coordinator | 01a085570c447273a54294de2d99bfcf armed; next 20:14:29 JST |
| 2026-09-09 20:01:53 JST | host-reconstitute-14635-mini | completed | worker-1 | reduced mini collect/run pass 8.4.1-9.1.1; no HA clone; HOLD no View |
| 2026-09-09 20:01:53 JST | host-reconstitute-14694 | started | worker-2 | rootdir subdirectory doctest; HOLD not PASS |
| 2026-09-09 20:01:53 JST | host-reconstitute-14694 | completed | worker-2 | pass 8.4.1-9.0.3; NameError 9.1.0/9.1.1; HOLD no View |
| 2026-09-09 20:01:53 JST | leftover-snippet-screen-1959 | completed | worker-2 | 14807/14921/14118 PR HOLD; no PASS |
| 2026-09-09 20:01:53 JST | version-matrix-1959 | completed | worker-3 | 14635 all versions same pass; HOLD |
| 2026-09-09 20:01:53 JST | contamination-2000 | started | worker-1 | contamination 0 |
| 2026-09-09 20:01:53 JST | no-worktrees-2000 | started | worker-2 | no worktrees in run dir |
| 2026-09-09 20:01:53 JST | no-collect-2000 | started | worker-3 | no expand/other resume |
| 2026-09-09 20:01:53 JST | contamination-2000 | completed | worker-1 | contamination clean |
| 2026-09-09 20:01:53 JST | no-worktrees-2000 | completed | worker-2 | no worktrees |
| 2026-09-09 20:01:53 JST | no-collect-2000 | completed | worker-3 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:01:53 JST | keep0-2000 | started | worker-1 | KEEP 0; HOLD extras |
| 2026-09-09 20:01:53 JST | no-dream-2000 | started | worker-2 | no isomorphic Dream 0004 |
| 2026-09-09 20:01:53 JST | no-save-2000 | started | worker-3 | 保全/HARD_STOP not before 08:00/09:00 |
| 2026-09-09 20:01:53 JST | keep0-2000 | completed | worker-1 | HOLD not PASS |
| 2026-09-09 20:01:53 JST | no-dream-2000 | completed | worker-2 | THIN_WRAPPER stopped |
| 2026-09-09 20:01:53 JST | no-save-2000 | completed | worker-3 | operate/work continues |
| 2026-09-09 20:01:53 JST | pre-2014 | started | worker-1 | 20:14 tick takes next non-Dream job |
| 2026-09-09 20:01:53 JST | pre-2014 | completed | worker-1 | vacancy continues until 08:00 保全 |
| 2026-09-09 20:02:53 JST | host-reconstitute-14877 | started | worker-3 | plugin dir() sizes; HOLD not PASS |
| 2026-09-09 20:02:53 JST | host-reconstitute-14877 | completed | worker-3 | 32 plugins dir_sum 1609-1701; HOLD no View |
| 2026-09-09 20:02:53 JST | contamination-2002 | started | worker-1 | contamination 0 |
| 2026-09-09 20:02:53 JST | contamination-2002 | completed | worker-1 | contamination clean |
| 2026-09-09 20:02:53 JST | hold-stay-2002 | started | worker-2 | HOLD stays HOLD; no 保全 yet |
| 2026-09-09 20:02:53 JST | hold-stay-2002 | completed | worker-2 | no HOLD→PASS; KEEP 0 |
| 2026-09-09 20:03:26 JST | host-reconstitute-13985 | completed | worker-1 | 13985 [tool.pytest] string addopts TypeError 9.x; list form pass; 8.4.1 ignores table; HOLD no View |
| 2026-09-09 20:03:26 JST | leftover-hold-trees-2000 | completed | worker-2 | 13913 sqlalchemy clone / 14700 jaraco / 14762 3.15b4 CI / 9298 Windows remain HOLD; no extra trees; no PASS |
| 2026-09-09 20:03:26 JST | leftover-snippet-screen-1959 | completed | worker-2 | leftover public snippets screened; 13985 実機 HOLD; trees remain HOLD |
| 2026-09-09 20:03:26 JST | version-matrix-1959 | completed | worker-3 | 13985 8.4.1/9.0.1/9.1.1 matrix recorded; HOLD no View |
| 2026-09-09 20:03:26 JST | clock-gate-1959 | completed | coordinator | operate/work; 20:00 vacancy filled |
| 2026-09-09 20:03:26 JST | scheduler-confirm-1959 | completed | coordinator | 01a085570c447273a54294de2d99bfcf still 15m; next ~20:14 |
| 2026-09-09 20:04:27 JST | clock-gate-2004 | started | coordinator | operate/work; occupy now not wait 20:14 |
| 2026-09-09 20:04:27 JST | leftover-reconstitute-2004 | started | worker-1 | next leftover public snippets; HOLD not PASS |
| 2026-09-09 20:04:27 JST | leftover-reconstitute-2004b | started | worker-2 | next leftover public snippets; HOLD not PASS |
| 2026-09-09 20:04:27 JST | leftover-reconstitute-2004c | started | worker-3 | next leftover public snippets; HOLD not PASS |
| 2026-09-09 20:07:51 JST | clock-gate-2004 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:07:51 JST | host-reconstitute-14973 | started | worker-1 | addModuleCleanup flag; HOLD not PASS |
| 2026-09-09 20:07:51 JST | host-reconstitute-14973 | completed | worker-1 | unittest writes flag; pytest 8.4.1-9.1.1 missing; HOLD no View |
| 2026-09-09 20:07:51 JST | host-reconstitute-14812 | started | worker-2 | caplog teardown makereport; HOLD not PASS |
| 2026-09-09 20:07:51 JST | host-reconstitute-14812 | completed | worker-2 | INTERNALERROR KeyError 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 20:07:51 JST | host-reconstitute-14702 | started | worker-3 | fixture doctest; HOLD not PASS |
| 2026-09-09 20:07:51 JST | host-reconstitute-14702 | completed | worker-3 | 3.14 2 pass 1 skip no INTERNALERROR; HOLD no View |
| 2026-09-09 20:07:51 JST | leftover-reconstitute-2004 | completed | worker-1 | 14973 HOLD no View |
| 2026-09-09 20:07:51 JST | leftover-reconstitute-2004b | completed | worker-2 | 14812 HOLD no View |
| 2026-09-09 20:07:51 JST | leftover-reconstitute-2004c | completed | worker-3 | 14702 HOLD no View |
| 2026-09-09 20:07:51 JST | leftover-pr-hold-2006 | started | worker-1 | 13796/14453/14210/14777/14348/14811/14750 HOLD notes |
| 2026-09-09 20:07:51 JST | leftover-pr-hold-2006 | completed | worker-1 | PRs stay HOLD; 正解 off Dreamer |
| 2026-09-09 20:07:51 JST | contamination-2006 | started | worker-2 | contamination 0 |
| 2026-09-09 20:07:51 JST | no-collect-2006 | started | worker-3 | no expand/other resume |
| 2026-09-09 20:07:51 JST | contamination-2006 | completed | worker-2 | contamination clean |
| 2026-09-09 20:07:51 JST | no-collect-2006 | completed | worker-3 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:07:51 JST | no-dream-2006 | started | worker-1 | no isomorphic Dream 0004 |
| 2026-09-09 20:07:51 JST | no-save-2006 | started | worker-2 | 保全/HARD_STOP not before 08:00/09:00 |
| 2026-09-09 20:07:51 JST | keep0-2006 | started | worker-3 | KEEP 0; HOLD extras |
| 2026-09-09 20:07:51 JST | no-dream-2006 | completed | worker-1 | THIN_WRAPPER stopped |
| 2026-09-09 20:07:51 JST | no-save-2006 | completed | worker-2 | operate/work continues |
| 2026-09-09 20:07:51 JST | keep0-2006 | completed | worker-3 | HOLD not PASS |
| 2026-09-09 20:08:53 JST | host-reconstitute-13922 | started | worker-2 | UserWarning file_or_dir probe; HOLD |
| 2026-09-09 20:08:53 JST | host-reconstitute-13922 | completed | worker-2 | 3.14 rc=4 no UserWarning; HOLD no View |
| 2026-09-09 20:08:53 JST | contamination-2008 | started | worker-1 | contamination 0 |
| 2026-09-09 20:08:53 JST | contamination-2008 | completed | worker-1 | contamination clean |
| 2026-09-09 20:08:53 JST | no-dream-2008 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 20:08:53 JST | no-dream-2008 | completed | worker-3 | THIN_WRAPPER stopped; KEEP 0 |
| 2026-09-09 20:09:19 JST | leftover-comment-hold-2009 | started | worker-1 | 12689/13834/14388/14420/14624/14670/13993 HOLD notes |
| 2026-09-09 20:09:19 JST | leftover-comment-hold-2009 | completed | worker-1 | HOLD not PASS; no extra trees |
| 2026-09-09 20:09:19 JST | pre-2014b | started | worker-2 | 20:14 tick next non-Dream; no wait |
| 2026-09-09 20:09:19 JST | pre-2014b | completed | worker-2 | vacancy continues until 08:00 保全 |
| 2026-09-09 20:09:19 JST | hold-stay-2009 | started | worker-3 | HOLD stays HOLD; KEEP 0 |
| 2026-09-09 20:09:19 JST | hold-stay-2009 | completed | worker-3 | no HOLD→PASS; no 保全 |
| 2026-09-09 20:10:29 JST | clock-gate-2010 | started | coordinator | operate/work; occupy 20:14 tick now |
| 2026-09-09 20:10:29 JST | scheduler-confirm-2010 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 20:14:29 |
| 2026-09-09 20:10:29 JST | leftover-reconstitute-2010a | started | worker-1 | next leftover public snippet; HOLD not PASS |
| 2026-09-09 20:10:29 JST | leftover-reconstitute-2010b | started | worker-2 | next leftover public snippet; HOLD not PASS |
| 2026-09-09 20:10:29 JST | leftover-reconstitute-2010c | started | worker-3 | next leftover public snippet; HOLD not PASS |
| 2026-09-09 20:13:55 JST | clock-gate-2010 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:13:55 JST | scheduler-confirm-2010 | completed | coordinator | 01a085570c447273a54294de2d99bfcf armed 15m |
| 2026-09-09 20:13:55 JST | host-reconstitute-14807 | started | worker-1 | custom TOML [pytest] via -c; HOLD not PASS |
| 2026-09-09 20:13:55 JST | host-reconstitute-14807 | completed | worker-1 | -c [pytest] ignored 8.4.1-9.1.1; pytest.toml from 9.0.1; HOLD no View |
| 2026-09-09 20:13:55 JST | host-reconstitute-14514b | started | worker-2 | python_files *.test.py; HOLD not PASS |
| 2026-09-09 20:13:55 JST | host-reconstitute-14514b | completed | worker-2 | still ModuleNotFoundError pkg.foo; HOLD no View |
| 2026-09-09 20:13:55 JST | host-reconstitute-14255 | started | worker-3 | quoted vs int log_cli_level; HOLD not PASS |
| 2026-09-09 20:13:55 JST | host-reconstitute-14255 | completed | worker-3 | quoted INFO pass; int TypeError on 9.x; HOLD no View |
| 2026-09-09 20:13:55 JST | host-refute-14973-enter | started | worker-1 | enterModuleContext flag; HOLD |
| 2026-09-09 20:13:55 JST | host-refute-14973-enter | completed | worker-1 | unittest exited; pytest entered not exited; HOLD no View |
| 2026-09-09 20:13:55 JST | leftover-reconstitute-2010a | completed | worker-1 | 14807 HOLD no View |
| 2026-09-09 20:13:55 JST | leftover-reconstitute-2010b | completed | worker-2 | 14514b HOLD no View |
| 2026-09-09 20:13:55 JST | leftover-reconstitute-2010c | completed | worker-3 | 14255 HOLD no View |
| 2026-09-09 20:13:55 JST | contamination-2014 | started | worker-1 | contamination 0 |
| 2026-09-09 20:13:55 JST | no-worktrees-2014 | started | worker-2 | no worktrees in run dir |
| 2026-09-09 20:13:55 JST | no-collect-2014 | started | worker-3 | no expand/other resume |
| 2026-09-09 20:13:55 JST | contamination-2014 | completed | worker-1 | contamination clean |
| 2026-09-09 20:13:55 JST | no-worktrees-2014 | completed | worker-2 | no worktrees |
| 2026-09-09 20:13:55 JST | no-collect-2014 | completed | worker-3 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:13:55 JST | keep0-2014 | started | worker-1 | KEEP 0; HOLD extras |
| 2026-09-09 20:13:55 JST | no-dream-2014 | started | worker-2 | no isomorphic Dream 0004 |
| 2026-09-09 20:13:55 JST | no-save-2014 | started | worker-3 | 保全/HARD_STOP not before 08:00/09:00 |
| 2026-09-09 20:13:55 JST | keep0-2014 | completed | worker-1 | HOLD not PASS |
| 2026-09-09 20:13:55 JST | no-dream-2014 | completed | worker-2 | THIN_WRAPPER stopped |
| 2026-09-09 20:13:55 JST | no-save-2014 | completed | worker-3 | operate/work continues |
| 2026-09-09 20:15:43 JST | clock-gate-2015 | started | coordinator | operate/work; occupy now not wait 20:29 |
| 2026-09-09 20:15:43 JST | leftover-reconstitute-2015a | started | worker-1 | next leftover host-verify; HOLD not PASS |
| 2026-09-09 20:15:43 JST | leftover-reconstitute-2015b | started | worker-2 | version-matrix fills; HOLD not PASS |
| 2026-09-09 20:15:43 JST | leftover-reconstitute-2015c | started | worker-3 | leftover HOLD screens; HOLD not PASS |
| 2026-09-09 20:18:38 JST | leftover-reconstitute-2015a | completed | worker-1 | 14389 raises match-fail During handling on 8.4.1/9.0.1 omitted 9.1.1; HOLD no View |
| 2026-09-09 20:18:38 JST | leftover-reconstitute-2015b | completed | worker-2 | 14389 8.4.1/9.0.1/9.1.1 matrix; HOLD no View |
| 2026-09-09 20:18:38 JST | leftover-reconstitute-2015c | completed | worker-3 | 13913/14700/14762/9298 remain HOLD without extra trees; no PASS |
| 2026-09-09 20:18:38 JST | clock-gate-2015 | completed | coordinator | operate/work; 20:16 vacancy filled not wait 20:29 |
| 2026-09-09 20:18:52 JST | clock-gate-2015 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:18:52 JST | host-reconstitute-14807-both | started | worker-1 | both TOML tables + pyproject [pytest]; HOLD |
| 2026-09-09 20:18:52 JST | host-reconstitute-14807-both | completed | worker-1 | no UsageError; ini_options wins; pyproject [pytest] ignored; HOLD no View |
| 2026-09-09 20:18:52 JST | host-reconstitute-14514-importlib | started | worker-2 | import-mode=importlib; HOLD |
| 2026-09-09 20:18:52 JST | host-reconstitute-14514-importlib | completed | worker-2 | importlib collect rc=0; default ImportError; HOLD no View |
| 2026-09-09 20:18:52 JST | version-matrix-2015 | started | worker-3 | 13922/14255/13985/14877/14973 extra versions; HOLD |
| 2026-09-09 20:18:52 JST | version-matrix-2015 | completed | worker-3 | same splits; HOLD no View |
| 2026-09-09 20:18:52 JST | leftover-reconstitute-2015a | completed | worker-1 | 14807 extra HOLD no View |
| 2026-09-09 20:18:52 JST | leftover-reconstitute-2015b | completed | worker-2 | version-matrix HOLD no View |
| 2026-09-09 20:18:52 JST | leftover-reconstitute-2015c | completed | worker-3 | 13927/13998/14182/14264/14433/13875/14389 HOLD notes |
| 2026-09-09 20:18:52 JST | contamination-2017 | started | worker-1 | contamination 0 |
| 2026-09-09 20:18:52 JST | no-collect-2017 | started | worker-2 | no expand/other resume |
| 2026-09-09 20:18:52 JST | no-dream-2017 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 20:18:52 JST | contamination-2017 | completed | worker-1 | contamination clean |
| 2026-09-09 20:18:52 JST | no-collect-2017 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:18:52 JST | no-dream-2017 | completed | worker-3 | THIN_WRAPPER stopped; KEEP 0; no 保全 |
| 2026-09-09 20:19:44 JST | host-refute-14514-importlib-run | started | worker-2 | importlib run not just collect; HOLD |
| 2026-09-09 20:19:44 JST | host-refute-14514-importlib-run | completed | worker-2 | 8.4.1/9.1.1 run rc=0 1 passed; HOLD no View |
| 2026-09-09 20:19:44 JST | leftover-comment-hold-2019 | started | worker-1 | 13724/13727/13778/13976/14205/14269/14271/14285/14391/14393 HOLD notes |
| 2026-09-09 20:19:44 JST | leftover-comment-hold-2019 | completed | worker-1 | HOLD not PASS |
| 2026-09-09 20:19:44 JST | contamination-2019 | started | worker-3 | contamination 0 |
| 2026-09-09 20:19:44 JST | contamination-2019 | completed | worker-3 | contamination clean; no Dream 0004; no 保全 |
| 2026-09-09 20:19:44 JST | pre-2029 | started | worker-1 | 20:29 tick next non-Dream; no wait |
| 2026-09-09 20:19:44 JST | pre-2029 | completed | worker-1 | vacancy continues until 08:00 保全 |
| 2026-09-09 20:22:39 JST | clock-gate-2021 | started | coordinator | operate/work; first R1 chain exists; no isomorphic 0004 |
| 2026-09-09 20:22:39 JST | host-refute-14389-extra | started | worker-1 | 14389 9.0.3/9.1.0 During-handling; HOLD not PASS |
| 2026-09-09 20:22:39 JST | verify-runpair-2021 | started | worker-2 | test_runpair twice into scratch; not Dreamer |
| 2026-09-09 20:22:39 JST | verify-hdd-run-2021 | started | worker-3 | test_hdd_run twice into scratch; not Dreamer |
| 2026-09-09 20:25:00 JST | clock-gate-2021 | completed | coordinator | operate/work; CHAIN-001/002/003 exist; no 0004 |
| 2026-09-09 20:25:00 JST | host-refute-14389-extra | completed | worker-1 | During handling 8.4.1/9.0.1/9.0.3; omitted 9.1.0; HOLD no View |
| 2026-09-09 20:25:00 JST | verify-runpair-2021 | completed | worker-2 | test_runpair 12 OK twice scratch |
| 2026-09-09 20:25:00 JST | verify-hdd-run-2021 | completed | worker-3 | test_hdd_run 25 OK twice scratch |
| 2026-09-09 20:25:00 JST | verify-other-eco-2021 | started | worker-2 | test_other_ecosystems_recipe |
| 2026-09-09 20:25:00 JST | verify-other-eco-2021 | completed | worker-2 | 4 OK |
| 2026-09-09 20:25:00 JST | host-refute-14514-importlib-extra | started | worker-1 | importlib 9.0.1-9.1.0; HOLD |
| 2026-09-09 20:25:00 JST | host-refute-14514-importlib-extra | completed | worker-1 | rc=0 1 passed; HOLD no View |
| 2026-09-09 20:25:00 JST | contamination-2022 | started | worker-3 | contamination 0 |
| 2026-09-09 20:25:00 JST | no-dream-2022 | started | worker-2 | no isomorphic Dream 0004 |
| 2026-09-09 20:25:00 JST | contamination-2022 | completed | worker-3 | contamination clean |
| 2026-09-09 20:25:00 JST | no-dream-2022 | completed | worker-2 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 20:25:00 JST | pre-2029b | started | worker-1 | 20:29 next non-Dream; no wait |
| 2026-09-09 20:25:00 JST | pre-2029b | completed | worker-1 | vacancy continues until 08:00 保全 |
| 2026-09-09 20:25:49 JST | host-refute-14807-devnull | started | worker-3 | -c /dev/null collect; HOLD |
| 2026-09-09 20:25:49 JST | host-refute-14807-devnull | completed | worker-3 | 8.4.1/9.1.1 rc=0 collect; HOLD no View |
| 2026-09-09 20:25:49 JST | keep0-2025 | started | worker-1 | KEEP 0; first R1 exists; no 0004 |
| 2026-09-09 20:25:49 JST | keep0-2025 | completed | worker-1 | HOLD not PASS; no 保全 |
| 2026-09-09 20:28:41 JST | clock-gate-2028 | started | coordinator | operate/work; occupy 13913/14700/14762/9298 now |
| 2026-09-09 20:28:41 JST | host-reconstitute-13913 | started | worker-1 | testpaths+python_files+idents mini; HOLD not PASS |
| 2026-09-09 20:28:41 JST | host-reconstitute-14700 | started | worker-2 | fixture doctest reports.py line; HOLD not PASS; no jaraco clone |
| 2026-09-09 20:28:41 JST | host-reconstitute-14762-9298 | started | worker-3 | 3.15 segfault / Windows pycache_prefix host probe; HOLD not PASS |
| 2026-09-09 20:31:44 JST | clock-gate-2028 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:31:44 JST | host-reconstitute-13913 | completed | worker-1 | testpaths+idents 8.4.1 pass / pytest9 unrecognized; HOLD no View |
| 2026-09-09 20:31:44 JST | host-reconstitute-14700 | completed | worker-2 | 3.14 skip no INTERNALERROR; HOLD no View |
| 2026-09-09 20:31:44 JST | host-reconstitute-14762-9298 | completed | worker-3 | 3.14 no segfault; macOS pyc present; HOLD no View |
| 2026-09-09 20:31:44 JST | contamination-2030 | started | worker-1 | contamination 0 |
| 2026-09-09 20:31:44 JST | no-collect-2030 | started | worker-2 | no expand/other resume |
| 2026-09-09 20:31:44 JST | no-dream-2030 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 20:31:44 JST | contamination-2030 | completed | worker-1 | contamination clean |
| 2026-09-09 20:31:44 JST | no-collect-2030 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:31:44 JST | no-dream-2030 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 20:33:11 JST | host-reconstitute-13755 | started | worker-1 | 13755 session heavy_fixture re-init public snippet; HOLD; not Dreamer |
| 2026-09-09 20:33:20 JST | clock-gate-2032 | started | coordinator | operate/work; occupy now not wait 20:44 |
| 2026-09-09 20:33:20 JST | host-reconstitute-14811 | started | worker-1 | string ini list deprecation probe; HOLD not PASS |
| 2026-09-09 20:33:20 JST | host-reconstitute-13913-extra | started | worker-2 | 13913 python_files list vs omit; HOLD not PASS |
| 2026-09-09 20:33:20 JST | host-reconstitute-14613-env | started | worker-3 | PYTEST_CACHE_DIR_BASE getenv/--help; HOLD not PASS |
| 2026-09-09 20:34:23 JST | host-reconstitute-13755 | completed | worker-1 | 13755 session heavy_fixture 4 params/10 setups 8.4.1/9.0.1/9.1.1; HOLD no View |
| 2026-09-09 20:35:25 JST | clock-gate-2032 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:35:25 JST | host-reconstitute-14811 | completed | worker-1 | no PytestRemovedIn10Warning; AssertionError list; HOLD no View |
| 2026-09-09 20:35:25 JST | host-reconstitute-13913-extra | completed | worker-2 | list/omit python_files same 8.4.1 pass / pytest9 unrecognized; HOLD no View |
| 2026-09-09 20:35:25 JST | host-reconstitute-14613-env | completed | worker-3 | PYTEST_CACHE_DIR_BASE unset; help has cache_dir only; HOLD no View |
| 2026-09-09 20:35:25 JST | contamination-2034 | started | worker-1 | contamination 0 |
| 2026-09-09 20:35:25 JST | no-collect-2034 | started | worker-2 | no expand/other resume |
| 2026-09-09 20:35:25 JST | no-dream-2034 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 20:35:25 JST | contamination-2034 | completed | worker-1 | contamination clean |
| 2026-09-09 20:35:25 JST | no-collect-2034 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:35:25 JST | no-dream-2034 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 20:37:13 JST | clock-gate-2036 | started | coordinator | operate/work; occupy now not wait 20:44 |
| 2026-09-09 20:37:13 JST | host-refute-13755-extra | started | worker-1 | 13755 9.0.3/9.1.0 setups; HOLD not PASS |
| 2026-09-09 20:37:13 JST | host-reconstitute-14084 | started | worker-2 | --pyargs cwd mini; HOLD not PASS |
| 2026-09-09 20:37:13 JST | version-matrix-2036 | started | worker-3 | 14811/9298 extra versions; HOLD not PASS |
| 2026-09-09 20:39:13 JST | clock-gate-2036 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:39:13 JST | host-refute-13755-extra | completed | worker-1 | 9.0.3/9.1.0 4 params 10 setups; HOLD no View |
| 2026-09-09 20:39:13 JST | host-reconstitute-14084 | completed | worker-2 | subdir --pyargs needs PYTHONPATH=..; HOLD no View |
| 2026-09-09 20:39:13 JST | version-matrix-2036 | completed | worker-3 | 14811 no warning; 9298 pyc present 9.0.3/9.1.0; HOLD no View |
| 2026-09-09 20:39:13 JST | contamination-2038 | started | worker-1 | contamination 0 |
| 2026-09-09 20:39:13 JST | no-collect-2038 | started | worker-2 | no expand/other resume |
| 2026-09-09 20:39:13 JST | no-dream-2038 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 20:39:13 JST | contamination-2038 | completed | worker-1 | contamination clean |
| 2026-09-09 20:39:13 JST | no-collect-2038 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:39:13 JST | no-dream-2038 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 20:41:42 JST | clock-gate-2041 | started | coordinator | operate/work; occupy now not wait 20:44 |
| 2026-09-09 20:41:42 JST | host-reconstitute-14514-toplevel | started | worker-1 | top-level foo.test.py default vs importlib; HOLD not PASS |
| 2026-09-09 20:41:42 JST | host-refute-13885-extra | started | worker-2 | 13885 extra versions if needed; HOLD not PASS |
| 2026-09-09 20:41:42 JST | host-refute-14800-extra | started | worker-3 | 14800 extra versions if needed; HOLD not PASS |
| 2026-09-09 20:43:46 JST | clock-gate-2041 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:43:46 JST | host-reconstitute-14514-toplevel | completed | worker-1 | top-level foo.test.py default No module named foo; importlib 1 pass; HOLD no View |
| 2026-09-09 20:43:46 JST | host-refute-13885-extra | completed | worker-2 | 13885 already full matrix; filled 14084 903/910 instead; HOLD no View |
| 2026-09-09 20:43:46 JST | host-refute-14800-extra | completed | worker-3 | 14800 already full matrix; 14613-901 cache_dir + 13913 addopts; HOLD no View |
| 2026-09-09 20:43:46 JST | contamination-2043 | started | worker-1 | contamination 0 |
| 2026-09-09 20:43:46 JST | no-collect-2043 | started | worker-2 | no expand/other resume |
| 2026-09-09 20:43:46 JST | no-dream-2043 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 20:43:46 JST | contamination-2043 | completed | worker-1 | contamination clean |
| 2026-09-09 20:43:46 JST | no-collect-2043 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:43:46 JST | no-dream-2043 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 20:45:13 JST | clock-gate-2044 | started | coordinator | operate/work; occupy 20:44 tick now |
| 2026-09-09 20:45:13 JST | scheduler-confirm-2044 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 20:59:29 |
| 2026-09-09 20:45:13 JST | leftover-reconstitute-2044a | started | worker-1 | next leftover host-verify; HOLD not PASS |
| 2026-09-09 20:45:13 JST | leftover-reconstitute-2044b | started | worker-2 | version-matrix fill; HOLD not PASS |
| 2026-09-09 20:45:13 JST | leftover-reconstitute-2044c | started | worker-3 | leftover review/refute; HOLD not PASS |
| 2026-09-09 20:50:43 JST | clock-gate-2049 | started | coordinator | operate/work; occupy now not wait 21:00 |
| 2026-09-09 20:50:43 JST | host-refute-13699-extra | started | worker-1 | 13699 asynctest importorskip extra versions; HOLD not PASS |
| 2026-09-09 20:50:43 JST | host-refute-14094-MonkeyPatch | started | worker-2 | 14094 correct MonkeyPatch spelling control; HOLD not PASS |
| 2026-09-09 20:50:43 JST | host-refute-14447-911plain | started | worker-3 | 14447 9.1.1 --assert=plain; HOLD not PASS |
| 2026-09-09 20:55:06 JST | clock-gate-2049 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 20:55:06 JST | host-refute-13699-extra | completed | worker-1 | importorskip AttributeError 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 20:55:06 JST | host-refute-14094-MonkeyPatch | completed | worker-2 | MonkeyPatch 1 pass 2 fail restore-missing; HOLD no View |
| 2026-09-09 20:55:06 JST | host-refute-14447-911plain | completed | worker-3 | 9.1.1 --assert=plain 3 pass; HOLD no View |
| 2026-09-09 20:55:06 JST | host-reconstitute-11502 | started | worker-1 | /dev/null config rootdir; HOLD not PASS |
| 2026-09-09 20:55:06 JST | host-reconstitute-14705 | started | worker-2 | custom toml python_files; HOLD not PASS |
| 2026-09-09 20:55:06 JST | host-refute-14048-noinit-extra | started | worker-3 | 14048 903/910 noinit; HOLD not PASS |
| 2026-09-09 20:55:06 JST | host-reconstitute-11502 | completed | worker-1 | rootdir=/dev 8.4.1-9.1.1; no cache warning; HOLD no View |
| 2026-09-09 20:55:06 JST | host-reconstitute-14705 | completed | worker-2 | [pytest] ignored; [tool.pytest] from 9.0.1; HOLD no View |
| 2026-09-09 20:55:06 JST | host-refute-14048-noinit-extra | completed | worker-3 | 9.0.3/9.1.0 noinit rc=4; HOLD no View |
| 2026-09-09 20:55:06 JST | contamination-2053 | started | worker-1 | contamination 0 |
| 2026-09-09 20:55:06 JST | no-collect-2053 | started | worker-2 | no expand/other resume |
| 2026-09-09 20:55:06 JST | no-dream-2053 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 20:55:06 JST | contamination-2053 | completed | worker-1 | contamination clean |
| 2026-09-09 20:55:06 JST | no-collect-2053 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 20:55:06 JST | no-dream-2053 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 20:55:36 JST | clock-gate-2044 | completed | coordinator | operate/work; filled by 20:49 host 実機 |
| 2026-09-09 20:55:36 JST | scheduler-confirm-2044 | completed | coordinator | scheduler still 15m; no wait |
| 2026-09-09 20:55:36 JST | leftover-reconstitute-2044a | completed | worker-1 | 13699 extra + 11502; HOLD no View |
| 2026-09-09 20:55:36 JST | leftover-reconstitute-2044b | completed | worker-2 | 14094b + 14705; HOLD no View |
| 2026-09-09 20:55:36 JST | leftover-reconstitute-2044c | completed | worker-3 | 14447 911plain + 14048 noinit; HOLD no View |
| 2026-09-09 21:00:26 JST | clock-gate-2100 | started | coordinator | operate/work; occupy now not wait 21:14 |
| 2026-09-09 21:00:26 JST | host-refute-11502-run | started | worker-1 | 11502 run not collect-only; HOLD not PASS |
| 2026-09-09 21:00:26 JST | host-refute-14705-ini-options | started | worker-2 | 14705 [tool.pytest.ini_options]; HOLD not PASS |
| 2026-09-09 21:00:26 JST | host-reconstitute-leftover-2100 | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:01:11 JST | clock-gate-2057 | completed | coordinator | operate/work; occupy leftover reconstitution; no 保全 |
| 2026-09-09 21:01:11 JST | scheduler-confirm-2057 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 20:59:29 JST not waited |
| 2026-09-09 21:01:11 JST | leftover-reconstitute-2057a | completed | worker-1 | 14445/14819/14820/14101 RESULT matrices; HOLD no View |
| 2026-09-09 21:01:11 JST | leftover-reconstitute-2057b | completed | worker-2 | 14431 default collect skip all versions; 14608 extra layouts; HOLD no View |
| 2026-09-09 21:01:11 JST | leftover-reconstitute-2057c | completed | worker-3 | leftover PRs 14446..14921 HOLD 正解; no PASS |
| 2026-09-09 21:01:11 JST | contamination-2057 | completed | worker-1 | contamination clean |
| 2026-09-09 21:01:11 JST | no-collect-2057 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:01:11 JST | no-dream-2057 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:03:56 JST | clock-gate-2100 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 21:03:56 JST | host-refute-11502-run | completed | worker-1 | run /dev/null PytestCacheWarning 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:03:56 JST | host-refute-14705-ini-options | completed | worker-2 | custom -c ini_options read on 8.4.1; HOLD no View |
| 2026-09-09 21:03:56 JST | host-reconstitute-leftover-2100 | completed | worker-3 | 14716/14916/14814 HOLD no View |
| 2026-09-09 21:03:56 JST | host-reconstitute-14716 | started | worker-1 | -c invalid paths; HOLD not PASS |
| 2026-09-09 21:03:57 JST | host-reconstitute-14916 | started | worker-2 | rewrite introspection gaps; HOLD not PASS |
| 2026-09-09 21:03:57 JST | host-reconstitute-14814 | started | worker-3 | walrus/starred rewrite; HOLD not PASS |
| 2026-09-09 21:03:57 JST | host-reconstitute-14716 | completed | worker-1 | wrong ext silent; missing ini FileNotFoundError; HOLD no View |
| 2026-09-09 21:03:57 JST | host-reconstitute-14916 | completed | worker-2 | lists+f() already introspect; HOLD no View |
| 2026-09-09 21:03:57 JST | host-reconstitute-14814 | completed | worker-3 | starred rewrite (9,[9]); walrus-tuple pass; HOLD no View |
| 2026-09-09 21:03:57 JST | contamination-2102 | started | worker-1 | contamination 0 |
| 2026-09-09 21:03:57 JST | no-collect-2102 | started | worker-2 | no expand/other resume |
| 2026-09-09 21:03:57 JST | no-dream-2102 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 21:03:57 JST | contamination-2102 | completed | worker-1 | contamination clean |
| 2026-09-09 21:03:57 JST | no-collect-2102 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:03:57 JST | no-dream-2102 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:04:14 JST | leftover-reconstitute-2102a | completed | worker-1 | 14608c tests/ --db-url 9.1.0 unrecognized; 8.4.1-9.0.3 and 9.1.1 pass; HOLD no View |
| 2026-09-09 21:04:14 JST | leftover-reconstitute-2102b | completed | worker-2 | 14608c test_foo same 9.1.0 split; src/ unrecognized all; HOLD no View |
| 2026-09-09 21:04:14 JST | leftover-uv-pr-hold-2102 | completed | worker-3 | uv leftover PRs 16139/18406/18979/19114/19330/19370/19613/21265 HOLD; no PASS |
| 2026-09-09 21:04:14 JST | scheduler-confirm-2102 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:14:29 JST; do not wait |
| 2026-09-09 21:04:14 JST | contamination-2102 | completed | worker-1 | contamination clean |
| 2026-09-09 21:04:14 JST | no-collect-2102 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:04:14 JST | no-dream-2102 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:05:46 JST | leftover-refute-14608c-testing | completed | worker-1 | testing/ same 9.1.0 unrecognized split as tests/; HOLD no View |
| 2026-09-09 21:06:19 JST | leftover-refute-14608c-test | completed | worker-2 | test/ same 9.1.0 unrecognized; HOLD no View |
| 2026-09-09 21:10:23 JST | clock-gate-2108 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:10:23 JST | scheduler-confirm-2108 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:14:29 JST not waited |
| 2026-09-09 21:10:23 JST | leftover-reconstitute-2108a | completed | worker-1 | 14817 method-call rewrite bound-method intermediates 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:10:23 JST | leftover-reconstitute-2108b | completed | worker-2 | 14608c testpaths=tests does not rescue 9.1.0; tp_other 9.1.0 unrecognized; HOLD no View |
| 2026-09-09 21:10:23 JST | leftover-reconstitute-2108c | completed | worker-3 | 14816 IfExp / 14815 subscript no where line; 14813 test-only HOLD |
| 2026-09-09 21:10:23 JST | contamination-2108 | completed | worker-1 | contamination clean |
| 2026-09-09 21:10:23 JST | no-collect-2108 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:10:23 JST | no-dream-2108 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:11:16 JST | leftover-refute-14608c-argorder | completed | worker-1 | CLI tests path rescues 9.1.0 --db-url; test_it.py path unrecognized all versions; HOLD no View |
| 2026-09-09 21:15:03 JST | clock-gate-2113 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:15:03 JST | scheduler-confirm-2113 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:14:29 JST not waited |
| 2026-09-09 21:15:03 JST | leftover-reconstitute-2113a | completed | worker-1 | 14608c root conftest pass 9.1.0; nested tests/unit unrecognized all; HOLD no View |
| 2026-09-09 21:15:03 JST | leftover-reconstitute-2113b | completed | worker-2 | 14817 instance.compute still bound-method; 14608c 903 path order rc=5; HOLD no View |
| 2026-09-09 21:15:03 JST | leftover-review-2113c | completed | worker-3 | 14104/13976 leftover comments HOLD; 14591/14095 already reconstituted; no PASS |
| 2026-09-09 21:15:03 JST | contamination-2113 | completed | worker-1 | contamination clean |
| 2026-09-09 21:15:03 JST | no-collect-2113 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:15:03 JST | no-dream-2113 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:15:39 JST | clock-gate-2115 | started | coordinator | operate/work; occupy now not wait 21:29 |
| 2026-09-09 21:15:39 JST | host-reconstitute-leftover-2115a | started | worker-1 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:15:39 JST | host-reconstitute-leftover-2115b | started | worker-2 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:15:39 JST | host-reconstitute-leftover-2115c | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:15:50 JST | leftover-refute-14608c-inside-case | completed | worker-1 | tests/test_it.py still 9.1.0-only miss; Tests/ capital unrecognized 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:18:18 JST | clock-gate-2115 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 21:18:18 JST | host-reconstitute-leftover-2115a | completed | worker-1 | 9703 -c config autouse leak through 9.0.3; HOLD no View |
| 2026-09-09 21:18:18 JST | host-reconstitute-leftover-2115b | completed | worker-2 | 13246 sibling value shadow FAILED config::test2; HOLD no View |
| 2026-09-09 21:18:18 JST | host-reconstitute-leftover-2115c | completed | worker-3 | 14814 bare walrus pass; 14716 toml/cfg FileNotFound; 11502 nocache; HOLD no View |
| 2026-09-09 21:18:18 JST | contamination-2116 | started | worker-1 | contamination 0 |
| 2026-09-09 21:18:18 JST | no-collect-2116 | started | worker-2 | no expand/other resume |
| 2026-09-09 21:18:18 JST | no-dream-2116 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 21:18:18 JST | contamination-2116 | completed | worker-1 | contamination clean |
| 2026-09-09 21:18:18 JST | no-collect-2116 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:18:18 JST | no-dream-2116 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:19:50 JST | clock-gate-2118 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:19:50 JST | scheduler-confirm-2118 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:29:29 JST not waited |
| 2026-09-09 21:19:50 JST | leftover-reconstitute-2118a | completed | worker-1 | 14104 session gap 3 pass 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:19:50 JST | leftover-reconstitute-2118b | completed | worker-2 | 14608c test-foo/testdir/testfoo 9.1.0-only miss; _tests unrecognized all; HOLD no View |
| 2026-09-09 21:19:50 JST | leftover-review-2118c | completed | worker-3 | 13976 comment is 14591 duplicate HOLD; no PASS |
| 2026-09-09 21:19:50 JST | contamination-2118 | completed | worker-1 | contamination clean |
| 2026-09-09 21:19:50 JST | no-collect-2118 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:19:50 JST | no-dream-2118 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:20:22 JST | leftover-refute-21120 | completed | worker-1 | 14104 get 9.0.3 3 pass; 14608c testing123 9.1.0-only miss; HOLD no View |
| 2026-09-09 21:24:28 JST | clock-gate-2123 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:24:28 JST | scheduler-confirm-2123 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:29:29 JST not waited |
| 2026-09-09 21:24:28 JST | leftover-reconstitute-2123a | completed | worker-1 | 14271 monkeypatch hasattr True 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:24:28 JST | leftover-reconstitute-2123b | completed | worker-2 | 14104 setup-show carries session fixture; 14608c test_suite/test2/mytests; HOLD no View |
| 2026-09-09 21:24:28 JST | leftover-reconstitute-2123c | completed | worker-3 | 14476 -k foo collects mark+name 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:24:28 JST | contamination-2123 | completed | worker-1 | contamination clean |
| 2026-09-09 21:24:28 JST | no-collect-2123 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:24:28 JST | no-dream-2123 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:27:36 JST | clock-gate-2126 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:27:36 JST | scheduler-confirm-2126 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:29:29 JST not waited |
| 2026-09-09 21:27:36 JST | leftover-reconstitute-2126a | completed | worker-1 | 13957b MRE 8.4.1 b1-a1 vs pytest9 a1-b1; swap restores; HOLD no View |
| 2026-09-09 21:27:36 JST | leftover-reconstitute-2126b | completed | worker-2 | 13755b session fix_once torn down after test_a ERROR test_b all versions; HOLD no View |
| 2026-09-09 21:27:36 JST | leftover-reconstitute-2126c | completed | worker-3 | 14271 delitem raising=False then assign 1 pass 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:27:36 JST | contamination-2126 | completed | worker-1 | contamination clean |
| 2026-09-09 21:27:36 JST | no-collect-2126 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:27:36 JST | no-dream-2126 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:30:37 JST | clock-gate-2130 | started | coordinator | operate/work; occupy now not wait 21:44 |
| 2026-09-09 21:30:37 JST | host-reconstitute-leftover-2130a | started | worker-1 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:30:37 JST | host-reconstitute-leftover-2130b | started | worker-2 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:30:37 JST | host-reconstitute-leftover-2130c | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:30:56 JST | clock-gate-2130 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:30:56 JST | scheduler-confirm-2130 | completed | coordinator | 01a085570c447273a54294de2d99bfcf 21:29 fired; next ~21:44; not waited |
| 2026-09-09 21:30:56 JST | leftover-reconstitute-2130a | completed | worker-1 | 13957b run 4 pass 8.4.1-9.1.1; swap 9.1.0 b-first; HOLD no View |
| 2026-09-09 21:30:56 JST | leftover-reconstitute-2130b | completed | worker-2 | 13755 setup-show session teardown between param groups same 8.4.1/9.1.1; HOLD no View |
| 2026-09-09 21:30:56 JST | leftover-review-2130c | completed | worker-3 | 14447 leftover eval-order comment already in tree 3 fail rewrite / 3 pass plain; HOLD |
| 2026-09-09 21:30:56 JST | contamination-2130 | completed | worker-1 | contamination clean |
| 2026-09-09 21:30:56 JST | no-collect-2130 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:30:56 JST | no-dream-2130 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:32:47 JST | clock-gate-2130 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 21:32:47 JST | host-reconstitute-leftover-2130a | completed | worker-1 | 9703b config::test_same collapse + --lf reruns both; HOLD no View |
| 2026-09-09 21:32:47 JST | host-reconstitute-leftover-2130b | completed | worker-2 | 9703 --rootdir=. unique nodeids; HOLD no View |
| 2026-09-09 21:32:47 JST | host-reconstitute-leftover-2130c | completed | worker-3 | 13246 subdir still FAILED ../config::test2; HOLD no View |
| 2026-09-09 21:32:47 JST | contamination-2131 | started | worker-1 | contamination 0 |
| 2026-09-09 21:32:47 JST | no-collect-2131 | started | worker-2 | no expand/other resume |
| 2026-09-09 21:32:48 JST | no-dream-2131 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 21:32:48 JST | contamination-2131 | completed | worker-1 | contamination clean |
| 2026-09-09 21:32:48 JST | no-collect-2131 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:32:48 JST | no-dream-2131 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:33:37 JST | clock-gate-2133 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:33:37 JST | scheduler-confirm-2133 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:44:29 JST not waited |
| 2026-09-09 21:33:37 JST | leftover-reconstitute-2133a | completed | worker-1 | 13976 fixture-params override 9.1.0-only duplicate; 9.1.1 restored; HOLD no View |
| 2026-09-09 21:33:37 JST | leftover-reconstitute-2133b | completed | worker-2 | 13957b -v nodeids match collect b1-a1 vs a1-b1; HOLD no View |
| 2026-09-09 21:33:37 JST | leftover-reconstitute-2133c | completed | worker-3 | 13755b 4 SETUP/TEARDOWN S fix_once 8.4.1 and 9.1.1; HOLD no View |
| 2026-09-09 21:33:37 JST | contamination-2133 | completed | worker-1 | contamination clean |
| 2026-09-09 21:33:37 JST | no-collect-2133 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:33:37 JST | no-dream-2133 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:36:15 JST | clock-gate-2135 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:36:15 JST | scheduler-confirm-2135 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:44:29 JST not waited |
| 2026-09-09 21:36:15 JST | leftover-reconstitute-2135a | completed | worker-1 | 13976 conftest layout same 9.1.0 duplicate; HOLD no View |
| 2026-09-09 21:36:15 JST | leftover-reconstitute-2135b | completed | worker-2 | 13976 generate_tests workaround 5 pass including 9.1.0; HOLD not a product |
| 2026-09-09 21:36:15 JST | leftover-reconstitute-2135c | completed | worker-3 | 14608c confcutdir=. does not rescue 9.1.0; HOLD no View |
| 2026-09-09 21:36:15 JST | contamination-2135 | completed | worker-1 | contamination clean |
| 2026-09-09 21:36:15 JST | no-collect-2135 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:36:15 JST | no-dream-2135 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:41:13 JST | clock-gate-2139 | completed | coordinator | operate/work; occupy leftover now; no 保全 |
| 2026-09-09 21:41:13 JST | scheduler-confirm-2139 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:44:29 JST not waited |
| 2026-09-09 21:41:13 JST | leftover-reconstitute-2139a | completed | worker-1 | 14650b isolated no-strict auto-suffix 2 pass 8.4.1-9.1.1; HOLD no View |
| 2026-09-09 21:41:13 JST | leftover-reconstitute-2139b | completed | worker-2 | 13976 ids= still 9.1.0 duplicate; HOLD no View |
| 2026-09-09 21:41:14 JST | leftover-reconstitute-2139c | completed | worker-3 | 14800 setup-show _finalizers after skip teardown 9.1.0; HOLD no View |
| 2026-09-09 21:41:14 JST | contamination-2139 | completed | worker-1 | contamination clean |
| 2026-09-09 21:41:14 JST | no-collect-2139 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:41:14 JST | no-dream-2139 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:45:22 JST | clock-gate-2144 | started | coordinator | operate/work; occupy now not wait 21:59 |
| 2026-09-09 21:45:22 JST | host-reconstitute-leftover-2144a | started | worker-1 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:45:22 JST | host-reconstitute-leftover-2144b | started | worker-2 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:45:22 JST | host-reconstitute-leftover-2144c | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 21:47:34 JST | clock-gate-2144 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 21:47:34 JST | host-reconstitute-leftover-2144a | completed | worker-1 | 14004b testpaths leak 8.4.1-9.0.3 gone 9.1.0; HOLD no View |
| 2026-09-09 21:47:34 JST | host-reconstitute-leftover-2144b | completed | worker-2 | 9703b --rootdir=. --lf only failed file; HOLD no View |
| 2026-09-09 21:47:34 JST | host-reconstitute-leftover-2144c | completed | worker-3 | explicit path 14004b no leak all versions; HOLD no View |
| 2026-09-09 21:47:34 JST | contamination-2146 | started | worker-1 | contamination 0 |
| 2026-09-09 21:47:34 JST | no-collect-2146 | started | worker-2 | no expand/other resume |
| 2026-09-09 21:47:34 JST | no-dream-2146 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 21:47:34 JST | contamination-2146 | completed | worker-1 | contamination clean |
| 2026-09-09 21:47:34 JST | no-collect-2146 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:47:34 JST | no-dream-2146 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:48:54 JST | clock-gate-2148 | started | coordinator | operate/work; occupy leftover now not wait 21:59 |
| 2026-09-09 21:48:54 JST | scheduler-confirm-2148 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 21:59:29 JST not waited |
| 2026-09-09 21:48:54 JST | leftover-reconstitute-2148a | started | worker-1 | 14608c pythonpath leftover; HOLD not PASS |
| 2026-09-09 21:48:54 JST | leftover-reconstitute-2148b | started | worker-2 | 14608c addopts/noconftest/confcutdir leftover; HOLD not PASS |
| 2026-09-09 21:48:54 JST | leftover-reconstitute-2148c | started | worker-3 | 14431 python_files + 14800 setup-show 9.0.1 leftover; HOLD not PASS |
| 2026-09-09 21:54:15 JST | clock-gate-2148 | completed | coordinator | operate/work; occupy leftover now not wait 21:59 |
| 2026-09-09 21:54:15 JST | scheduler-confirm-2148 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:59:29 JST not waited |
| 2026-09-09 21:54:15 JST | leftover-reconstitute-2148a | completed | worker-1 | 14608c pythonpath/-o/ini_options do not rescue 9.1.0; HOLD no View |
| 2026-09-09 21:54:15 JST | leftover-reconstitute-2148b | completed | worker-2 | 14608c addopts=tests rescues 9.1.0; noconftest unrecognized all; confcutdir=tests no rescue; HOLD no View |
| 2026-09-09 21:54:15 JST | leftover-reconstitute-2148c | completed | worker-3 | 14431 python_files=test.py 1 pass all; 14800 setup-show 9.0.1 2pass1skip; setup-plan no tests ran; HOLD no View |
| 2026-09-09 21:54:15 JST | leftover-reconstitute-2152a | completed | worker-1 | 14608c addopts inside tests/ 1 pass including 9.1.0; HOLD no View |
| 2026-09-09 21:54:15 JST | leftover-reconstitute-2152b | completed | worker-2 | 14608c norecursedirs=tests does not rescue 9.1.0; HOLD no View |
| 2026-09-09 21:54:15 JST | leftover-reconstitute-2152c | completed | worker-3 | 14694 pythonpath still NameError 9.1.0/9.1.1; HOLD no View |
| 2026-09-09 21:54:15 JST | contamination-2154 | completed | worker-1 | contamination clean |
| 2026-09-09 21:54:15 JST | no-collect-2154 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:54:15 JST | no-dream-2154 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:55:55 JST | leftover-reconstitute-2156a | completed | worker-1 | 14608c pythonpath inside tests/ still 9.1.0 unrecognized; HOLD no View |
| 2026-09-09 21:55:55 JST | leftover-reconstitute-2156b | completed | worker-2 | 14608c collect_ignore=tests does not rescue 9.1.0; HOLD no View |
| 2026-09-09 21:55:55 JST | leftover-reconstitute-2156c | completed | worker-3 | 14004b pythonpath still leak 8.4.1-9.0.3 gone 9.1.0; HOLD no View |
| 2026-09-09 21:57:13 JST | leftover-reconstitute-2157a | completed | worker-1 | 14608c consider_namespace_packages does not rescue 9.1.0; HOLD no View |
| 2026-09-09 21:57:13 JST | leftover-reconstitute-2157b | completed | worker-2 | 13913 pythonpath still pytest9 unrecognized --db --write-idents; HOLD no View |
| 2026-09-09 21:57:13 JST | leftover-reconstitute-2157c | completed | worker-3 | 14514 pythonpath still ModuleNotFound foo.test; importlib 1 pass; HOLD no View |
| 2026-09-09 21:57:13 JST | contamination-2157 | completed | worker-1 | contamination clean |
| 2026-09-09 21:57:13 JST | no-collect-2157 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 21:57:13 JST | no-dream-2157 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 21:58:31 JST | leftover-reconstitute-2158a | completed | worker-1 | 14696 pythonpath existing idents still unrecognized all versions; HOLD no View |
| 2026-09-09 21:58:31 JST | leftover-reconstitute-2158b | completed | worker-2 | 14696 pythonpath missing file still 9.1.0-only unrecognized; HOLD no View |
| 2026-09-09 21:58:31 JST | leftover-reconstitute-2158c | completed | worker-3 | leftover uv PRs still HOLD no sealed files; cargo leftover 0; HOLD not PASS |
| 2026-09-09 21:58:31 JST | scheduler-confirm-2158 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 21:59:29 JST not waited |
| 2026-09-09 22:00:18 JST | clock-gate-2159 | started | coordinator | operate/work; occupy now not wait 22:14 |
| 2026-09-09 22:00:18 JST | host-reconstitute-leftover-2159a | started | worker-1 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:00:18 JST | host-reconstitute-leftover-2159b | started | worker-2 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:00:18 JST | host-reconstitute-leftover-2159c | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:01:33 JST | clock-gate-2201 | started | coordinator | operate/work; occupy leftover now not wait 22:14 |
| 2026-09-09 22:01:33 JST | scheduler-confirm-2201 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:14:29 JST not waited |
| 2026-09-09 22:01:33 JST | leftover-reconstitute-2201a | started | worker-1 | 14807 extras native table / pytest.toml ini_options; HOLD not PASS |
| 2026-09-09 22:01:33 JST | leftover-reconstitute-2201b | started | worker-2 | 14807 extras pytest.ini / named both-tables; HOLD not PASS |
| 2026-09-09 22:01:33 JST | leftover-review-2201c | started | worker-3 | leftover pytest 正解 PRs + uv HOLD PRs; HOLD not PASS |
| 2026-09-09 22:03:02 JST | clock-gate-2159 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 22:03:02 JST | host-reconstitute-leftover-2159a | completed | worker-1 | 12083 overlap collect 1 on 8.4.1 / 2 on pytest 9; HOLD no View |
| 2026-09-09 22:03:02 JST | host-reconstitute-leftover-2159b | completed | worker-2 | 13925 empty/dot alone ZeroDivision all; a/ 1 pass; HOLD no View |
| 2026-09-09 22:03:02 JST | host-reconstitute-leftover-2159c | completed | worker-3 | 14004b --rootdir=. still leak; --rootdir=.. rc=5; HOLD no View |
| 2026-09-09 22:03:02 JST | contamination-2201 | started | worker-1 | contamination 0 |
| 2026-09-09 22:03:02 JST | no-collect-2201 | started | worker-2 | no expand/other resume |
| 2026-09-09 22:03:02 JST | no-dream-2201 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 22:03:02 JST | contamination-2201 | completed | worker-1 | contamination clean |
| 2026-09-09 22:03:02 JST | no-collect-2201 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:03:02 JST | no-dream-2201 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:04:57 JST | clock-gate-2201 | completed | coordinator | operate/work; occupy leftover now not wait 22:14 |
| 2026-09-09 22:04:57 JST | scheduler-confirm-2201 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:14:29 JST not waited |
| 2026-09-09 22:04:57 JST | leftover-reconstitute-2201a | completed | worker-1 | 14807 pyproject native list from 9.0.1; string TypeError 9.x; HOLD no View |
| 2026-09-09 22:04:57 JST | leftover-reconstitute-2201b | completed | worker-2 | 14807 pytest.toml only [pytest]; native+ini_options UsageError on 9; HOLD no View |
| 2026-09-09 22:04:57 JST | leftover-review-2201c | completed | worker-3 | leftover pytest 正解 PRs + uv 8 fences=0 HOLD; 14821 is 14820; HOLD not PASS |
| 2026-09-09 22:04:57 JST | leftover-reconstitute-2205a | completed | worker-1 | 14807 tox.ini/setup.cfg/pytest.ini all versions; HOLD no View |
| 2026-09-09 22:04:57 JST | leftover-reconstitute-2205b | completed | worker-2 | 14807 -c INI [pytest] all versions; -c TOML native from 9.0.1; HOLD no View |
| 2026-09-09 22:04:57 JST | contamination-2205 | completed | worker-1 | contamination clean |
| 2026-09-09 22:04:57 JST | no-collect-2205 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:04:57 JST | no-dream-2205 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:06:23 JST | leftover-reconstitute-2206a | completed | worker-1 | 12083 reverse args still 8.4.1 n=1 pytest9 n=2; HOLD no View |
| 2026-09-09 22:06:23 JST | leftover-reconstitute-2206b | completed | worker-2 | 12083 subdirectory vs tests 8.4.1 drops parent; HOLD no View |
| 2026-09-09 22:06:23 JST | leftover-reconstitute-2206c | completed | worker-3 | 12083 run overlap 1 pass 8.4.1 / 2 pass pytest9; HOLD no View |
| 2026-09-09 22:06:23 JST | leftover-reconstitute-2206d | completed | worker-1 | 14807 pytest.cfg filename ignored all versions; HOLD no View |
| 2026-09-09 22:08:26 JST | clock-gate-2208 | started | coordinator | operate/work; occupy leftover now not wait 22:14 |
| 2026-09-09 22:08:26 JST | scheduler-confirm-2208 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:14:29 JST not waited |
| 2026-09-09 22:08:26 JST | leftover-reconstitute-2208a | started | worker-1 | 13925 reverse empty-path leftover; HOLD not PASS |
| 2026-09-09 22:08:26 JST | leftover-reconstitute-2208b | started | worker-2 | 14807 setup.cfg [pytest] / ini_options string leftover; HOLD not PASS |
| 2026-09-09 22:08:26 JST | leftover-reconstitute-2208c | started | worker-3 | 12083 keep-duplicates reverse + two file args leftover; HOLD not PASS |
| 2026-09-09 22:10:19 JST | clock-gate-2208 | completed | coordinator | operate/work; occupy leftover now not wait 22:14 |
| 2026-09-09 22:10:19 JST | scheduler-confirm-2208 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:14:29 JST not waited |
| 2026-09-09 22:10:19 JST | leftover-reconstitute-2208a | completed | worker-1 | 13925 reverse a/ empty same 8/9; -- a/ 1 pass all; HOLD no View |
| 2026-09-09 22:10:19 JST | leftover-reconstitute-2208b | completed | worker-2 | 14807 setup.cfg [pytest] Failed all; ini_options string works all; pytest.toml string TypeError 9; HOLD no View |
| 2026-09-09 22:10:19 JST | leftover-reconstitute-2208c | completed | worker-3 | 12083 keep-duplicates reverse n=3 all; two file args n=2 all; HOLD no View |
| 2026-09-09 22:10:19 JST | leftover-review-2208d | completed | worker-1 | HOLD 14264/14348/13993/13834 no new sealed mini; HOLD not PASS |
| 2026-09-09 22:10:19 JST | contamination-2208 | completed | worker-1 | contamination clean |
| 2026-09-09 22:10:19 JST | no-collect-2208 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:10:19 JST | no-dream-2208 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:11:02 JST | leftover-reconstitute-2211a | completed | worker-1 | 12083 keep-duplicates subdirectory vs tests n=3 all; HOLD no View |
| 2026-09-09 22:12:20 JST | clock-gate-2212 | started | coordinator | operate/work; occupy leftover now not wait 22:14 |
| 2026-09-09 22:12:20 JST | scheduler-confirm-2212 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:14:29 JST not waited |
| 2026-09-09 22:12:20 JST | leftover-reconstitute-2212a | started | worker-1 | 14608c PYTEST_ADDOPTS=tests leftover; HOLD not PASS |
| 2026-09-09 22:12:20 JST | leftover-reconstitute-2212b | started | worker-2 | 13925 a/ . leftover; HOLD not PASS |
| 2026-09-09 22:12:20 JST | leftover-reconstitute-2212c | started | worker-3 | 14807 tox.ini [tool:pytest] leftover; HOLD not PASS |
| 2026-09-09 22:14:15 JST | clock-gate-2212 | completed | coordinator | operate/work; occupy leftover now not wait 22:14 |
| 2026-09-09 22:14:15 JST | scheduler-confirm-2212 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:14:29 JST not waited |
| 2026-09-09 22:14:15 JST | leftover-reconstitute-2212a | completed | worker-1 | 14608c PYTEST_ADDOPTS=tests rescues 9.1.0 like addopts; HOLD no View |
| 2026-09-09 22:14:15 JST | leftover-reconstitute-2212b | completed | worker-2 | 13925 a/ . and . a/ same 8/9 cwd-overlap drop; HOLD no View |
| 2026-09-09 22:14:15 JST | leftover-reconstitute-2212c | completed | worker-3 | 14807 tox.ini [tool:pytest] ignored; pytest.ini [tool:pytest] ignored; HOLD no View |
| 2026-09-09 22:14:15 JST | contamination-2214 | completed | worker-1 | contamination clean |
| 2026-09-09 22:14:15 JST | no-collect-2214 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:14:15 JST | no-dream-2214 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:15:30 JST | leftover-reconstitute-2215a | completed | worker-1 | 12083 tests . n=2 unique all versions; HOLD no View |
| 2026-09-09 22:15:30 JST | leftover-review-2215b | completed | worker-2 | HOLD 13778/13724/13927/14285/14391 no sealed mini; HOLD not PASS |
| 2026-09-09 22:16:22 JST | clock-gate-2215 | started | coordinator | operate/work; occupy now not wait 22:29 |
| 2026-09-09 22:16:22 JST | host-reconstitute-leftover-2215a | started | worker-1 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:16:22 JST | host-reconstitute-leftover-2215b | started | worker-2 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:16:22 JST | host-reconstitute-leftover-2215c | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:17:56 JST | clock-gate-2217 | started | coordinator | operate/work; occupy leftover now not wait 22:29 |
| 2026-09-09 22:17:56 JST | scheduler-confirm-2217 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:29:29 JST not waited |
| 2026-09-09 22:17:56 JST | leftover-reconstitute-2217a | started | worker-1 | 14412 ini_options times leftover; HOLD not PASS |
| 2026-09-09 22:17:56 JST | leftover-reconstitute-2217b | started | worker-2 | 14640 reverse interleaved leftover; HOLD not PASS |
| 2026-09-09 22:17:56 JST | leftover-reconstitute-2217c | started | worker-3 | 14148 cache_on 8.4.1 leftover; HOLD not PASS |
| 2026-09-09 22:18:58 JST | clock-gate-2215 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 22:18:58 JST | host-reconstitute-leftover-2215a | completed | worker-1 | 13704 dir/file overlap 1 vs 2; same file twice 2 vs 1; HOLD no View |
| 2026-09-09 22:18:58 JST | host-reconstitute-leftover-2215b | completed | worker-2 | 12083 overlap run 1 vs 2; keep-duplicates run 3; HOLD no View |
| 2026-09-09 22:18:58 JST | host-reconstitute-leftover-2215c | completed | worker-3 | 13925 collect-only '' a/ same 8/9 split; HOLD no View |
| 2026-09-09 22:18:58 JST | contamination-2217 | started | worker-1 | contamination 0 |
| 2026-09-09 22:18:58 JST | no-collect-2217 | started | worker-2 | no expand/other resume |
| 2026-09-09 22:18:58 JST | no-dream-2217 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 22:18:58 JST | contamination-2217 | completed | worker-1 | contamination clean |
| 2026-09-09 22:18:58 JST | no-collect-2217 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:18:58 JST | no-dream-2217 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:20:10 JST | clock-gate-2217 | completed | coordinator | operate/work; occupy leftover now not wait 22:29 |
| 2026-09-09 22:20:10 JST | scheduler-confirm-2217 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:29:29 JST not waited |
| 2026-09-09 22:20:10 JST | leftover-reconstitute-2217a | completed | worker-1 | 14412 ini_options/pytest.ini times 8.4.1 whole-test ms; pytest9 later 0.000us; HOLD no View |
| 2026-09-09 22:20:10 JST | leftover-reconstitute-2217b | completed | worker-2 | 14640 reverse interleaved 9.1.0 miss later assignment; setup-show no re-SETUP 9.1.0; HOLD no View |
| 2026-09-09 22:20:10 JST | leftover-reconstitute-2217c | completed | worker-3 | 14148 cache_on 8.4.1 1 pass; AttributeError only no:cacheprovider; HOLD no View |
| 2026-09-09 22:20:10 JST | leftover-review-2219 | completed | worker-1 | HOLD 13998/14182/14269/14393/14433 no sealed mini; HOLD not PASS |
| 2026-09-09 22:20:10 JST | contamination-2219 | completed | worker-1 | contamination clean |
| 2026-09-09 22:20:10 JST | no-collect-2219 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:20:10 JST | no-dream-2219 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:22:28 JST | clock-gate-2222 | started | coordinator | operate/work; occupy leftover now not wait 22:29 |
| 2026-09-09 22:22:28 JST | scheduler-confirm-2222 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:29:29 JST not waited |
| 2026-09-09 22:22:28 JST | leftover-reconstitute-2222a | started | worker-1 | 14971 reverse/setup-show leftover; HOLD not PASS |
| 2026-09-09 22:22:28 JST | leftover-reconstitute-2222b | started | worker-2 | 14964 reverse CASE1/setup-show leftover; HOLD not PASS |
| 2026-09-09 22:22:28 JST | leftover-reconstitute-2222c | started | worker-3 | 13704 keep-duplicates leftover; HOLD not PASS |
| 2026-09-09 22:24:11 JST | clock-gate-2222 | completed | coordinator | operate/work; occupy leftover now not wait 22:29 |
| 2026-09-09 22:24:11 JST | scheduler-confirm-2222 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:29:29 JST not waited |
| 2026-09-09 22:24:11 JST | leftover-reconstitute-2222a | completed | worker-1 | 14971 reverse 9.1.0 miss later services; setup-show no re-SETUP 9.1.0; HOLD no View |
| 2026-09-09 22:24:11 JST | leftover-reconstitute-2222b | completed | worker-2 | 14964 reverse CASE1 later test_a passes 9.1.0; setup-show drops autouse after gap; HOLD no View |
| 2026-09-09 22:24:11 JST | leftover-reconstitute-2222c | completed | worker-3 | 13704 keep-duplicates dir/file n=3 all; same-file twice n=2 all; HOLD no View |
| 2026-09-09 22:24:11 JST | contamination-2224 | completed | worker-1 | contamination clean |
| 2026-09-09 22:24:11 JST | no-collect-2224 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:24:11 JST | no-dream-2224 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:24:53 JST | leftover-reconstitute-2225a | completed | worker-1 | 13704 keep-duplicates RUN 3 pass all versions; HOLD no View |
| 2026-09-09 22:24:53 JST | leftover-reconstitute-2225b | completed | worker-2 | 14971 sorted 9.1.0 3 pass; HOLD no View |
| 2026-09-09 22:27:10 JST | clock-gate-2227 | started | coordinator | operate/work; occupy leftover now not wait 22:29 |
| 2026-09-09 22:27:10 JST | scheduler-confirm-2227 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:29:29 JST not waited |
| 2026-09-09 22:27:10 JST | leftover-reconstitute-2227a | started | worker-1 | 14640/14971 directory collect leftover; HOLD not PASS |
| 2026-09-09 22:27:10 JST | leftover-reconstitute-2227b | started | worker-2 | 14964 tests/ dir and no-gap leftover; HOLD not PASS |
| 2026-09-09 22:27:10 JST | leftover-reconstitute-2227c | started | worker-3 | 14104 setup-show 9.0.1/9.0.3 leftover; HOLD not PASS |
| 2026-09-09 22:29:09 JST | clock-gate-2227 | completed | coordinator | operate/work; occupy leftover now not wait 22:29 |
| 2026-09-09 22:29:09 JST | scheduler-confirm-2227 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:29:29 JST not waited |
| 2026-09-09 22:29:09 JST | leftover-reconstitute-2227a | completed | worker-1 | 14640 tests/ 3 pass all; 14971 services/ 2 pass all; HOLD no View |
| 2026-09-09 22:29:09 JST | leftover-reconstitute-2227b | completed | worker-2 | 14964 tests/ rc=5; no-gap both ERROR all; python_files=*.py dir both ERROR; HOLD no View |
| 2026-09-09 22:29:09 JST | leftover-reconstitute-2227c | completed | worker-3 | 14104 setup-show 9.0.1/9.0.3 session carry across gap; HOLD no View |
| 2026-09-09 22:29:09 JST | contamination-2229 | completed | worker-1 | contamination clean |
| 2026-09-09 22:29:09 JST | no-collect-2229 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:29:09 JST | no-dream-2229 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:31:31 JST | clock-gate-2231 | started | coordinator | operate/work; occupy leftover now not wait 22:44 |
| 2026-09-09 22:31:31 JST | scheduler-confirm-2231 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:44:29 JST not waited |
| 2026-09-09 22:31:31 JST | leftover-reconstitute-2231a | started | worker-1 | 14640 assignment-only + 14971 one-services+gap leftover; HOLD not PASS |
| 2026-09-09 22:31:31 JST | leftover-reconstitute-2231b | started | worker-2 | 14964 one-file+gap leftover; HOLD not PASS |
| 2026-09-09 22:31:31 JST | leftover-reconstitute-2231c | started | worker-3 | 5203/13885 setup-show leftover; HOLD not PASS |
| 2026-09-09 22:31:33 JST | clock-gate-2230 | started | coordinator | operate/work; occupy now not wait 22:44 |
| 2026-09-09 22:31:33 JST | host-reconstitute-leftover-2230a | started | worker-1 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:31:33 JST | host-reconstitute-leftover-2230b | started | worker-2 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:31:33 JST | host-reconstitute-leftover-2230c | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:33:13 JST | clock-gate-2231 | completed | coordinator | operate/work; occupy leftover now not wait 22:44 |
| 2026-09-09 22:33:13 JST | scheduler-confirm-2231 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:44:29 JST not waited |
| 2026-09-09 22:33:13 JST | leftover-reconstitute-2231a | completed | worker-1 | 14640 assignment-only 2 pass all; 14971 one-services+gap 2 pass all; HOLD no View |
| 2026-09-09 22:33:13 JST | leftover-reconstitute-2231b | completed | worker-2 | 14964 one-file+gap still guard all versions; miss needs two tests/ files with gap; HOLD no View |
| 2026-09-09 22:33:13 JST | leftover-reconstitute-2231c | completed | worker-3 | 5203 setup-show b from first a all; 13885 setup-show skip from 9.1.0; HOLD no View |
| 2026-09-09 22:33:13 JST | contamination-2233 | completed | worker-1 | contamination clean |
| 2026-09-09 22:33:13 JST | no-collect-2233 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:33:13 JST | no-dream-2233 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:33:55 JST | clock-gate-2230 | completed | coordinator | operate/work; hard_end not extended |
| 2026-09-09 22:33:55 JST | host-reconstitute-leftover-2230a | completed | worker-1 | 7777 nested collect 5; keep-duplicates still 5; HOLD no View |
| 2026-09-09 22:33:55 JST | host-reconstitute-leftover-2230b | completed | worker-2 | 13704b a/b a/ 1 vs 3; a/a before a/b on pytest 9; HOLD no View |
| 2026-09-09 22:33:55 JST | host-reconstitute-leftover-2230c | completed | worker-3 | 14964d test_* names still 9.1.0 gap miss; HOLD no View |
| 2026-09-09 22:33:55 JST | contamination-2232 | started | worker-1 | contamination 0 |
| 2026-09-09 22:33:55 JST | no-collect-2232 | started | worker-2 | no expand/other resume |
| 2026-09-09 22:33:55 JST | no-dream-2232 | started | worker-3 | no isomorphic Dream 0004 |
| 2026-09-09 22:33:55 JST | contamination-2232 | completed | worker-1 | contamination clean |
| 2026-09-09 22:33:55 JST | no-collect-2232 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:33:55 JST | no-dream-2232 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:36:15 JST | clock-gate-2236 | started | coordinator | operate/work; occupy leftover now not wait 22:44 |
| 2026-09-09 22:36:15 JST | scheduler-confirm-2236 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:44:29 JST not waited |
| 2026-09-09 22:36:15 JST | leftover-reconstitute-2236a | started | worker-1 | 14095/13755 setup-show leftover; HOLD not PASS |
| 2026-09-09 22:36:15 JST | leftover-reconstitute-2236b | started | worker-2 | 13704b keep-duplicates leftover; HOLD not PASS |
| 2026-09-09 22:36:15 JST | leftover-reconstitute-2236c | started | worker-3 | 7777 a/b collect leftover; HOLD not PASS |
| 2026-09-09 22:37:57 JST | clock-gate-2236 | completed | coordinator | operate/work; occupy leftover now not wait 22:44 |
| 2026-09-09 22:37:57 JST | scheduler-confirm-2236 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:44:29 JST not waited |
| 2026-09-09 22:37:57 JST | leftover-reconstitute-2236a | completed | worker-1 | 14095 setup-show same 5203; 13755 setup-show 901/903/910 10 S; HOLD no View |
| 2026-09-09 22:37:57 JST | leftover-reconstitute-2236b | completed | worker-2 | 13704b keep-duplicates a/b a/ n=4 all; HOLD no View |
| 2026-09-09 22:37:57 JST | leftover-reconstitute-2236c | completed | worker-3 | 7777 a/b n=3 a/b/c n=2 all; 14964d reverse gap 9.1.0 miss; HOLD no View |
| 2026-09-09 22:37:57 JST | contamination-2238 | completed | worker-1 | contamination clean |
| 2026-09-09 22:37:57 JST | no-collect-2238 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:37:57 JST | no-dream-2238 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:40:58 JST | clock-gate-2241 | started | coordinator | operate/work; occupy leftover now not wait 22:44 |
| 2026-09-09 22:40:58 JST | scheduler-confirm-2241 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:44:29 JST not waited |
| 2026-09-09 22:40:58 JST | leftover-reconstitute-2241a | started | worker-1 | 2043 collect-only leftover; HOLD not PASS |
| 2026-09-09 22:40:58 JST | leftover-reconstitute-2241b | started | worker-2 | 7777 a/ vs a/b overlap leftover; HOLD not PASS |
| 2026-09-09 22:40:58 JST | leftover-reconstitute-2241c | started | worker-3 | 14964d setup-show + 13704b run leftover; HOLD not PASS |
| 2026-09-09 22:48:05 JST | clock-gate-2241 | completed | coordinator | operate/work; occupy leftover now not wait 22:59 |
| 2026-09-09 22:48:05 JST | scheduler-confirm-2241 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:59:29 JST not waited |
| 2026-09-09 22:48:05 JST | leftover-reconstitute-2241a | completed | worker-1 | 2043 collect-only same split as run; HOLD no View |
| 2026-09-09 22:48:05 JST | leftover-reconstitute-2241b | completed | worker-2 | 7777 a/b a/ overlap collect 8.4.1 n=3 / pytest 9 n=5; HOLD no View |
| 2026-09-09 22:48:05 JST | leftover-reconstitute-2241c | completed | worker-3 | 14964d setup-show gap 9.1.0 drops later guard; 13704b run a/b a/ 1 vs 3 pass; HOLD no View |
| 2026-09-09 22:48:05 JST | clock-gate-2244 | started | coordinator | operate/work; occupy leftover now not wait 22:59 |
| 2026-09-09 22:48:05 JST | scheduler-confirm-2244 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:59:29 JST not waited |
| 2026-09-09 22:48:05 JST | leftover-reconstitute-2244a | started | worker-1 | 7777 RUN overlap leftover; HOLD not PASS |
| 2026-09-09 22:48:05 JST | leftover-reconstitute-2244b | started | worker-2 | 13704b RUN reverse + 13925 keep-duplicates leftover; HOLD not PASS |
| 2026-09-09 22:48:05 JST | leftover-reconstitute-2244c | started | worker-3 | 14964d/14640/14971 setup-show dir + 14775/14591 leftover; HOLD not PASS |
| 2026-09-09 22:48:12 JST | clock-gate-2246 | started | coordinator | operate/work; occupy now not wait 22:59 |
| 2026-09-09 22:48:12 JST | host-reconstitute-3062 | started | worker-1 | 3062 setup.cfg log_format; HOLD not PASS |
| 2026-09-09 22:48:12 JST | host-reconstitute-7777b | started | worker-2 | 7777 package-scoped fixtures; HOLD not PASS |
| 2026-09-09 22:48:12 JST | host-reconstitute-leftover-2246c | started | worker-3 | leftover public snippet; HOLD not PASS |
| 2026-09-09 22:58:19 JST | clock-gate-2246 | completed | coordinator | operate/work; occupy leftover now not wait 22:59 |
| 2026-09-09 22:58:19 JST | host-reconstitute-3062 | completed | worker-1 | setup.cfg log_format pytest raw getini + live-log; ConfigParser interpolation fail; HOLD no View |
| 2026-09-09 22:58:19 JST | host-reconstitute-7777b | completed | worker-2 | package-scoped pkg_a/pkg_b setup-show 3 pass all; HOLD no View |
| 2026-09-09 22:58:19 JST | host-reconstitute-leftover-2246c | completed | worker-3 | 14807 setup.cfg [tool:pytest] addopts=-q collect 1 all; HOLD no View |
| 2026-09-09 22:58:19 JST | contamination-2255 | completed | worker-1 | contamination clean |
| 2026-09-09 22:58:19 JST | no-collect-2255 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:58:19 JST | no-dream-2255 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:58:46 JST | clock-gate-2244 | completed | coordinator | operate/work; occupy leftover now not wait 22:59 |
| 2026-09-09 22:58:46 JST | scheduler-confirm-2244 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:59:29 JST not waited |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2244a | completed | worker-1 | 7777 overlap run 3 vs 5; keep-duplicates run 8 all; HOLD no View |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2244b | completed | worker-2 | 13704b run reverse 1 vs 3; 13925 keep-duplicates ZeroDivision on 8.4.1 too; 12083 tests . n=4; HOLD no View |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2244c | completed | worker-3 | 14775 -Werror _finalizers from 9.1.0; 13885 setup-plan lists autouse on 9.1.0; 14608c -o addopts rescues 9.1.0; HOLD no View |
| 2026-09-09 22:58:46 JST | contamination-2252 | completed | worker-1 | contamination clean |
| 2026-09-09 22:58:46 JST | no-collect-2252 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:58:46 JST | no-dream-2252 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:58:46 JST | clock-gate-2256 | started | coordinator | operate/work; occupy leftover now not wait 22:59 |
| 2026-09-09 22:58:46 JST | scheduler-confirm-2256 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 22:59:29 JST not waited |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2256a | started | worker-1 | 13784 setup-show leftover; HOLD not PASS |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2256b | started | worker-2 | 13976/14650 leftover; HOLD not PASS |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2256c | started | worker-3 | 14104 dir collect leftover; HOLD not PASS |
| 2026-09-09 22:58:46 JST | clock-gate-2256 | completed | coordinator | operate/work; occupy leftover now not wait 22:59 |
| 2026-09-09 22:58:46 JST | scheduler-confirm-2256 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 22:59:29 JST not waited |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2256a | completed | worker-1 | 13784 setup-show same doubling 8.4.1-9.0.3; HOLD no View |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2256b | completed | worker-2 | 13976 setup-show same 9.1.0 duplicate; 14650 collect-only same 8.4.1 suffix / 9.x duplicate; HOLD no View |
| 2026-09-09 22:58:46 JST | leftover-reconstitute-2256c | completed | worker-3 | 14104 dir collect 6 pass all; HOLD no View |
| 2026-09-09 22:58:46 JST | contamination-2257 | completed | worker-1 | contamination clean |
| 2026-09-09 22:58:46 JST | no-collect-2257 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 22:58:46 JST | no-dream-2257 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 22:59:41 JST | clock-gate-2259 | started | coordinator | operate/work; occupy leftover now not wait 22:59 |
| 2026-09-09 22:59:41 JST | leftover-reconstitute-2259a | started | worker-1 | 14011 setup-show leftover; HOLD not PASS |
| 2026-09-09 22:59:41 JST | leftover-reconstitute-2259b | started | worker-2 | 14691 setup-show leftover; HOLD not PASS |
| 2026-09-09 22:59:41 JST | leftover-reconstitute-2259c | started | worker-3 | 14048 pyargs collect leftover; HOLD not PASS |
| 2026-09-09 23:01:37 JST | clock-gate-2259 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:01:37 JST | leftover-reconstitute-2259a | completed | worker-1 | 14011 setup-show class fix per subclass still None; HOLD no View |
| 2026-09-09 23:01:37 JST | leftover-reconstitute-2259b | completed | worker-2 | 14691 setup-show sample not found; nocm 901/903/910 1 pass; HOLD no View |
| 2026-09-09 23:01:37 JST | leftover-reconstitute-2259c | completed | worker-3 | 14048 collect-only --pyargs with init 1 collected all; HOLD no View |
| 2026-09-09 23:01:37 JST | contamination-2300 | completed | worker-1 | contamination clean |
| 2026-09-09 23:01:37 JST | no-collect-2300 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:01:37 JST | no-dream-2300 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:01:37 JST | clock-gate-2301 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:01:37 JST | leftover-reconstitute-2301a | started | worker-1 | 13479 setup-show leftover; HOLD not PASS |
| 2026-09-09 23:01:37 JST | leftover-reconstitute-2301b | started | worker-2 | 14737 leftover extra versions; HOLD not PASS |
| 2026-09-09 23:01:40 JST | clock-gate-2300 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:01:40 JST | leftover-reconstitute-2300a | started | worker-1 | 13704b a/a a/ leftover; HOLD not PASS |
| 2026-09-09 23:01:40 JST | leftover-reconstitute-2300b | started | worker-2 | 7777 a/b2 a/ leftover; HOLD not PASS |
| 2026-09-09 23:01:40 JST | leftover-reconstitute-2300c | started | worker-3 | 14737 setup-show + 3062 escaped + 13925 empty-dot leftover; HOLD not PASS |
| 2026-09-09 23:03:48 JST | clock-gate-2301 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:03:48 JST | leftover-reconstitute-2301a | completed | worker-1 | 13479 setup-show ff not found all; HOLD no View |
| 2026-09-09 23:03:48 JST | leftover-reconstitute-2301b | completed | worker-2 | 14737 collect-only Function not skipped; conftest 901/910 still fail; module 841/901/910 skip; HOLD no View |
| 2026-09-09 23:03:48 JST | leftover-reconstitute-2301c | completed | worker-3 | 14447 setup-show still 3 fail all; HOLD no View |
| 2026-09-09 23:03:48 JST | contamination-2303 | completed | worker-1 | contamination clean |
| 2026-09-09 23:03:48 JST | no-collect-2303 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:03:48 JST | no-dream-2303 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:04:34 JST | clock-gate-2304 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:04:34 JST | leftover-reconstitute-2304a | started | worker-1 | 14084 leftover extras; HOLD not PASS |
| 2026-09-09 23:04:34 JST | leftover-reconstitute-2304b | started | worker-2 | 14392 extra is_fully_escaped; HOLD not PASS |
| 2026-09-09 23:04:34 JST | leftover-reconstitute-2304c | started | worker-3 | 14444 CLI capture leftover; HOLD not PASS |
| 2026-09-09 23:06:01 JST | clock-gate-2300 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:06:01 JST | leftover-reconstitute-2300a | completed | worker-1 | 13704b a/a a/ 1 vs 3 keep-duplicates 4; HOLD no View |
| 2026-09-09 23:06:01 JST | leftover-reconstitute-2300b | completed | worker-2 | 7777 a/b2 a/ 1 vs 5 keep-duplicates run 6; HOLD no View |
| 2026-09-09 23:06:01 JST | leftover-reconstitute-2300c | completed | worker-3 | 13925 empty-dot ZeroDivision all; 3062 escaped InterpolationSyntaxError; 14737 setup-show still fail; HOLD no View |
| 2026-09-09 23:06:01 JST | contamination-2303 | completed | worker-1 | contamination clean |
| 2026-09-09 23:06:01 JST | no-collect-2303 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:06:01 JST | no-dream-2303 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:06:38 JST | clock-gate-2304 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:06:38 JST | leftover-reconstitute-2304a | completed | worker-1 | 14084 subdir PYTHONPATH=. rc=4 903/910; collect-only matches run; HOLD no View |
| 2026-09-09 23:06:38 JST | leftover-reconstitute-2304b | completed | worker-2 | 14392 even-count backslash-dot False from 9.1.0; HOLD no View |
| 2026-09-09 23:06:38 JST | leftover-reconstitute-2304c | completed | worker-3 | 14444 CLI --capture=sys 1 pass all; hook append still fd; HOLD no View |
| 2026-09-09 23:06:38 JST | contamination-2305 | completed | worker-1 | contamination clean |
| 2026-09-09 23:06:38 JST | no-collect-2305 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:06:38 JST | no-dream-2305 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:07:28 JST | clock-gate-2307 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:07:28 JST | leftover-reconstitute-2307a | started | worker-1 | 13754 setup-show leftover; HOLD not PASS |
| 2026-09-09 23:07:28 JST | leftover-reconstitute-2307b | started | worker-2 | 13965 python_files leftover; HOLD not PASS |
| 2026-09-09 23:07:28 JST | leftover-reconstitute-2307c | started | worker-3 | 14811 leftover extra; HOLD not PASS |
| 2026-09-09 23:08:46 JST | clock-gate-2307 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:08:46 JST | leftover-reconstitute-2307a | completed | worker-1 | 13754 setup-show shared module same 8/9 4 pass; HOLD no View |
| 2026-09-09 23:08:46 JST | leftover-reconstitute-2307b | completed | worker-2 | 13965 python_files=test.py 1 pass all; HOLD no View |
| 2026-09-09 23:08:46 JST | leftover-reconstitute-2307c | completed | worker-3 | 14811 implicit dummy not the getini assert; HOLD no View |
| 2026-09-09 23:08:46 JST | contamination-2308 | completed | worker-1 | contamination clean |
| 2026-09-09 23:08:46 JST | no-collect-2308 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:08:46 JST | no-dream-2308 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:09:24 JST | clock-gate-2310 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:09:24 JST | leftover-reconstitute-2310a | started | worker-1 | 14389 assert=plain leftover; HOLD not PASS |
| 2026-09-09 23:09:24 JST | leftover-reconstitute-2310b | started | worker-2 | 14819 tb=short leftover; HOLD not PASS |
| 2026-09-09 23:10:07 JST | clock-gate-2310 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:10:07 JST | leftover-reconstitute-2310a | completed | worker-1 | 14389 --assert=plain drops During handling on 8.4.1 only; HOLD no View |
| 2026-09-09 23:10:07 JST | leftover-reconstitute-2310b | completed | worker-2 | 14819 --tb=short still 2 fail all; HOLD no View |
| 2026-09-09 23:10:07 JST | contamination-2310 | completed | worker-1 | contamination clean |
| 2026-09-09 23:10:07 JST | no-collect-2310 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:10:07 JST | no-dream-2310 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:10:42 JST | clock-gate-2311 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:10:42 JST | leftover-reconstitute-2311a | started | worker-1 | 14820 tb=short leftover; HOLD not PASS |
| 2026-09-09 23:11:35 JST | clock-gate-2311 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:11:35 JST | leftover-reconstitute-2311a | completed | worker-1 | 14820 --tb=short still 1 fail 1 pass; HOLD no View |
| 2026-09-09 23:11:35 JST | clock-gate-2312 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:11:35 JST | leftover-reconstitute-2312a | started | worker-1 | 14445 tb=short leftover; HOLD not PASS |
| 2026-09-09 23:12:16 JST | clock-gate-2312 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:12:16 JST | leftover-reconstitute-2312a | completed | worker-1 | 14445 --tb=short still 2 fail 1!=1 and 6==3; HOLD no View |
| 2026-09-09 23:12:16 JST | contamination-2312 | completed | worker-1 | contamination clean |
| 2026-09-09 23:12:16 JST | no-collect-2312 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:12:16 JST | no-dream-2312 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:12:38 JST | clock-gate-2313 | started | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:12:38 JST | leftover-reconstitute-2313a | started | worker-1 | 14816/14815 leftover extras; HOLD not PASS |
| 2026-09-09 23:13:34 JST | clock-gate-2313 | completed | coordinator | operate/work; occupy leftover now not wait 23:14 |
| 2026-09-09 23:13:34 JST | leftover-reconstitute-2313a | completed | worker-1 | 14816/14815 --tb=short still no where line; HOLD no View |
| 2026-09-09 23:13:34 JST | contamination-2313 | completed | worker-1 | contamination clean |
| 2026-09-09 23:13:34 JST | no-collect-2313 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:13:34 JST | no-dream-2313 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:17:26 JST | clock-gate-2316 | started | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:17:26 JST | scheduler-confirm-2316 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 23:29:29 JST not waited |
| 2026-09-09 23:17:27 JST | leftover-reconstitute-2316a | started | worker-1 | 13755b/13957b leftover extras; HOLD not PASS |
| 2026-09-09 23:17:27 JST | leftover-reconstitute-2316b | started | worker-2 | 14808/14812/14973 leftover extras; HOLD not PASS |
| 2026-09-09 23:17:27 JST | leftover-reconstitute-2316c | started | worker-3 | 14448/14814 leftover extras; HOLD not PASS |
| 2026-09-09 23:20:03 JST | clock-gate-2316 | completed | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:20:03 JST | scheduler-confirm-2316 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 23:29:29 JST not waited |
| 2026-09-09 23:20:03 JST | leftover-reconstitute-2316a | completed | worker-1 | 13755b setup-plan 4S/4T all; 13957b setup-show still 8/9 id swap; 14101 setup-show still XPASS; HOLD no View |
| 2026-09-09 23:20:03 JST | leftover-reconstitute-2316b | completed | worker-2 | 14808 collect-only 1 per layout; 14812 tb=short still INTERNALERROR; 14973 setup-show 2 pass cleanup still missing; HOLD no View |
| 2026-09-09 23:20:03 JST | leftover-reconstitute-2316c | completed | worker-3 | 14448 tb=short no where / plain AssertionError; 14814 tb=short starred still (9,[9]); HOLD no View |
| 2026-09-09 23:20:03 JST | clock-gate-2318 | started | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:20:03 JST | leftover-reconstitute-2318a | started | worker-1 | 14841/14488 leftover extras; HOLD not PASS |
| 2026-09-09 23:20:03 JST | leftover-reconstitute-2318b | started | worker-2 | 13985/14253/14092 leftover extras; HOLD not PASS |
| 2026-09-09 23:20:03 JST | leftover-reconstitute-2318c | started | worker-3 | 14650b/9703 leftover extras; HOLD not PASS |
| 2026-09-09 23:21:45 JST | clock-gate-2314 | started | coordinator | operate/work; vacancy leftover now not wait 23:29 |
| 2026-09-09 23:21:45 JST | leftover-reconstitute-2314a | started | worker-1 | 13704b sibling a/a a/b + same-dir twice; HOLD not PASS |
| 2026-09-09 23:21:45 JST | leftover-reconstitute-2314b | started | worker-2 | 7777 sibling a/b a/b2 + 12083/13925 same-dir twice; HOLD not PASS |
| 2026-09-09 23:21:45 JST | leftover-reconstitute-2314c | started | worker-3 | 3062 ini/full-escaped + 14807 named native+pytest + 14737 setup-plan; HOLD not PASS |
| 2026-09-09 23:23:13 JST | clock-gate-2318 | completed | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:23:13 JST | leftover-reconstitute-2318a | completed | worker-1 | 14841 tb=short still resource_tracker on 9; 14488 tb=short still StashKey; HOLD no View |
| 2026-09-09 23:23:13 JST | leftover-reconstitute-2318b | completed | worker-2 | 13985 collect-only TypeError string addopts on 9; 14253/14092 collect-only TypeError int native table on 9; HOLD no View |
| 2026-09-09 23:23:13 JST | leftover-reconstitute-2318c | completed | worker-3 | 14650b collect/show auto-suffix 2 pass; 9703 setup-show explicit files leak twice through 9.0.3 once from 9.1.0; HOLD no View |
| 2026-09-09 23:23:13 JST | contamination-2321 | completed | worker-1 | contamination clean |
| 2026-09-09 23:23:13 JST | no-collect-2321 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:23:13 JST | no-dream-2321 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:24:26 JST | clock-gate-2324 | started | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:24:26 JST | leftover-reconstitute-2324a | started | worker-1 | 14702/13246 leftover extras; HOLD not PASS |
| 2026-09-09 23:24:26 JST | leftover-reconstitute-2324b | started | worker-2 | 14613 leftover extras; HOLD not PASS |
| 2026-09-09 23:24:26 JST | leftover-reconstitute-2324c | started | worker-3 | 14004 leftover extras; HOLD not PASS |
| 2026-09-09 23:26:36 JST | clock-gate-2324 | completed | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:26:36 JST | leftover-reconstitute-2324a | completed | worker-1 | 14702 setup-show 2 pass 1 skip; 13246 setup-show still shadow; HOLD no View |
| 2026-09-09 23:26:36 JST | leftover-reconstitute-2324b | completed | worker-2 | 14613 no:cacheprovider -o cache_dir warning on 9 still 2 pass; HOLD no View |
| 2026-09-09 23:26:36 JST | leftover-reconstitute-2324c | completed | worker-3 | 14004 setup-show 4 pass no leak; HOLD no View |
| 2026-09-09 23:26:36 JST | clock-gate-2326 | started | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:26:36 JST | leftover-reconstitute-2326a | started | worker-1 | 14004b setup-show leftover; HOLD not PASS |
| 2026-09-09 23:27:27 JST | clock-gate-2326 | completed | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:27:27 JST | leftover-reconstitute-2326a | completed | worker-1 | 14004b setup-show inner 3 through 9.0.3 / 1 from 9.1.0; HOLD no View |
| 2026-09-09 23:27:27 JST | contamination-2327 | completed | worker-1 | contamination clean |
| 2026-09-09 23:27:27 JST | no-collect-2327 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:27:27 JST | no-dream-2327 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:28:16 JST | clock-gate-2328 | started | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:28:16 JST | leftover-reconstitute-2328a | started | worker-1 | 14560/14051/14323 leftover extras; HOLD not PASS |
| 2026-09-09 23:29:02 JST | clock-gate-2328 | completed | coordinator | operate/work; occupy leftover now not wait 23:29 |
| 2026-09-09 23:29:02 JST | leftover-reconstitute-2328a | completed | worker-1 | 14560 tb=short still KeyError; 14051 collect-only 1; 14323 setup-show 1 pass; HOLD no View |
| 2026-09-09 23:29:02 JST | contamination-2329 | completed | worker-1 | contamination clean |
| 2026-09-09 23:29:02 JST | no-collect-2329 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:29:02 JST | no-dream-2329 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:29:48 JST | clock-gate-2314 | completed | coordinator | operate/work; vacancy leftover now not wait 23:29 |
| 2026-09-09 23:29:48 JST | leftover-reconstitute-2314a | completed | worker-1 | 13704b sibling a/a a/b n=2 all; same-dir twice 3/6; 13704 tests/ tests/ 2/4; HOLD no View |
| 2026-09-09 23:29:48 JST | leftover-reconstitute-2314b | completed | worker-2 | 7777 sibling a/b a/b2 n=4; same-dir 5/10; 12083 tests tests 2/4; 13925 keep-duplicates '' . ZeroDivision all; HOLD no View |
| 2026-09-09 23:29:48 JST | leftover-reconstitute-2314c | completed | worker-3 | 3062 pytest.ini %% InterpolationSyntaxError; full-escaped ConfigParser ok / pytest literal %%; 14807 named pytest.toml no UsageError; 14737 setup-plan lists Function; HOLD no View |
| 2026-09-09 23:29:48 JST | contamination-2314 | completed | worker-1 | contamination clean |
| 2026-09-09 23:29:48 JST | no-collect-2314 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:29:48 JST | no-dream-2314 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:33:56 JST | clock-gate-2333 | started | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:33:56 JST | scheduler-confirm-2333 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 23:44:29 JST not waited |
| 2026-09-09 23:33:56 JST | leftover-reconstitute-2333a | started | worker-1 | 14811/14255 leftover extras; HOLD not PASS |
| 2026-09-09 23:33:56 JST | leftover-reconstitute-2333b | started | worker-2 | 14916/14705 leftover extras; HOLD not PASS |
| 2026-09-09 23:33:56 JST | leftover-reconstitute-2333c | started | worker-3 | 7777b/9703b leftover extras; HOLD not PASS |
| 2026-09-09 23:35:21 JST | clock-gate-2333 | completed | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:35:21 JST | scheduler-confirm-2333 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 23:44:29 JST not waited |
| 2026-09-09 23:35:21 JST | leftover-reconstitute-2333a | completed | worker-1 | 14811 collect-only 1; 14255 int collect-only TypeError on 9 quoted 1 all; HOLD no View |
| 2026-09-09 23:35:21 JST | leftover-reconstitute-2333b | completed | worker-2 | 14916 tb=short still introspects; 14705 collect-only same [pytest] vs [tool.pytest] split; HOLD no View |
| 2026-09-09 23:35:21 JST | leftover-reconstitute-2333c | completed | worker-3 | 7777b a/b a/ 1 vs 3 keep-duplicates 4; 9703b setup-show both test_same; HOLD no View |
| 2026-09-09 23:35:21 JST | contamination-2334 | completed | worker-1 | contamination clean |
| 2026-09-09 23:35:21 JST | no-collect-2334 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:35:21 JST | no-dream-2334 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:35:48 JST | clock-gate-2335 | started | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:35:48 JST | leftover-reconstitute-2335a | started | worker-1 | 14716 leftover extras; HOLD not PASS |
| 2026-09-09 23:35:48 JST | leftover-reconstitute-2335b | started | worker-2 | 14436/14094b leftover extras; HOLD not PASS |
| 2026-09-09 23:35:48 JST | leftover-reconstitute-2335c | started | worker-3 | 14608/13922 leftover extras; HOLD not PASS |
| 2026-09-09 23:36:35 JST | clock-gate-2335 | completed | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:36:35 JST | leftover-reconstitute-2335a | completed | worker-1 | 14716 setup-show 1 pass; missing toml/cfg FileNotFoundError; HOLD no View |
| 2026-09-09 23:36:35 JST | leftover-reconstitute-2335b | completed | worker-2 | 14094b tb=short still 2 fail 1 pass; 14436 parent collect name collision; HOLD no View |
| 2026-09-09 23:36:35 JST | leftover-reconstitute-2335c | completed | worker-3 | 14608 collect-only --from-b A rc=4 / A B n=2; 13922 collect-only extra rc=4 no UserWarning; HOLD no View |
| 2026-09-09 23:36:35 JST | contamination-2336 | completed | worker-1 | contamination clean |
| 2026-09-09 23:36:35 JST | no-collect-2336 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:36:35 JST | no-dream-2336 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:37:27 JST | clock-gate-2337 | started | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:37:27 JST | leftover-reconstitute-2337a | started | worker-1 | 14635/14700 leftover extras; HOLD not PASS |
| 2026-09-09 23:37:27 JST | leftover-reconstitute-2337b | started | worker-2 | 13882/14514b leftover extras; HOLD not PASS |
| 2026-09-09 23:37:27 JST | leftover-reconstitute-2337c | started | worker-3 | 11502 leftover extras; HOLD not PASS |
| 2026-09-09 23:38:13 JST | clock-gate-2337 | completed | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:38:13 JST | leftover-reconstitute-2337a | completed | worker-1 | 14635 setup-show 4 pass; 14700 setup-show 1 skip; HOLD no View |
| 2026-09-09 23:38:13 JST | leftover-reconstitute-2337b | completed | worker-2 | 13882 setup-show 2 pass; 14514b collect-only ImportError / importlib 1; HOLD no View |
| 2026-09-09 23:38:13 JST | leftover-reconstitute-2337c | completed | worker-3 | 11502 setup-show /dev/null nocache 1 pass; HOLD no View |
| 2026-09-09 23:38:13 JST | contamination-2338 | completed | worker-1 | contamination clean |
| 2026-09-09 23:38:13 JST | no-collect-2338 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:38:13 JST | no-dream-2338 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:39:14 JST | clock-gate-2339 | started | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:39:14 JST | leftover-reconstitute-2339a | started | worker-1 | 14514c leftover extras; HOLD not PASS |
| 2026-09-09 23:39:14 JST | leftover-reconstitute-2339b | started | worker-2 | 14683 leftover extras; HOLD not PASS |
| 2026-09-09 23:39:14 JST | leftover-reconstitute-2339c | started | worker-3 | 14608b leftover extras; HOLD not PASS |
| 2026-09-09 23:40:07 JST | clock-gate-2339 | completed | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:40:07 JST | leftover-reconstitute-2339a | completed | worker-1 | 14514c collect-only dir rc=5; explicit ImportError / importlib 1; HOLD no View |
| 2026-09-09 23:40:07 JST | leftover-reconstitute-2339b | completed | worker-2 | 14683 setup-show doctest 1 pass; HOLD no View |
| 2026-09-09 23:40:07 JST | leftover-reconstitute-2339c | completed | worker-3 | 14608b parent collect-only leftover name collision; HOLD no View |
| 2026-09-09 23:40:07 JST | contamination-2340 | completed | worker-1 | contamination clean |
| 2026-09-09 23:40:07 JST | no-collect-2340 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:40:07 JST | no-dream-2340 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:42:12 JST | clock-gate-2341 | started | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:42:12 JST | scheduler-confirm-2341 | started | coordinator | 01a085570c447273a54294de2d99bfcf next 23:44:29 JST not waited |
| 2026-09-09 23:42:12 JST | leftover-reconstitute-2341a | started | worker-1 | 14094/13957 leftover extras; HOLD not PASS |
| 2026-09-09 23:42:12 JST | leftover-reconstitute-2341b | started | worker-2 | 14148/14650c leftover extras; HOLD not PASS |
| 2026-09-09 23:42:12 JST | leftover-reconstitute-2341c | started | worker-3 | 13699/14877 leftover extras; HOLD not PASS |
| 2026-09-09 23:44:25 JST | clock-gate-2341 | completed | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:44:25 JST | scheduler-confirm-2341 | completed | coordinator | 01a085570c447273a54294de2d99bfcf next 23:44:29 JST not waited |
| 2026-09-09 23:44:25 JST | leftover-reconstitute-2341a | completed | worker-1 | 14094 tb=short Monkeypatch AttributeError; 13957 setup-show 1 pass no swap; HOLD no View |
| 2026-09-09 23:44:25 JST | leftover-reconstitute-2341b | completed | worker-2 | 14148 setup-show cache off AttributeError / on 1 pass; 14650c collect-only same 8 suffix / 9 ERROR; HOLD no View |
| 2026-09-09 23:44:25 JST | leftover-reconstitute-2341c | completed | worker-3 | 13699 without tree skip / with PYTHONPATH AttributeError; 14877 plugin count 32; HOLD no View |
| 2026-09-09 23:44:25 JST | clock-gate-2343 | started | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:44:25 JST | leftover-reconstitute-2343a | started | worker-1 | 14762/9298 leftover extras; HOLD not PASS |
| 2026-09-09 23:45:04 JST | clock-gate-2343 | completed | coordinator | operate/work; occupy leftover now not wait 23:44 |
| 2026-09-09 23:45:04 JST | leftover-reconstitute-2343a | completed | worker-1 | 14762 collect-only 1 no segfault; 9298 setup-show 1 pass; HOLD no View |
| 2026-09-09 23:45:04 JST | contamination-2344 | completed | worker-1 | contamination clean |
| 2026-09-09 23:45:04 JST | no-collect-2344 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:45:04 JST | no-dream-2344 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:45:42 JST | clock-gate-2345 | started | coordinator | operate/work; occupy leftover now not wait 23:59 |
| 2026-09-09 23:45:42 JST | leftover-reconstitute-2345a | started | worker-1 | 13913 leftover extras; HOLD not PASS |
| 2026-09-09 23:45:42 JST | leftover-reconstitute-2345b | started | worker-2 | 14431 leftover extras; HOLD not PASS |
| 2026-09-09 23:45:42 JST | leftover-reconstitute-2345c | started | worker-3 | 14412 leftover extras; HOLD not PASS |
| 2026-09-09 23:46:21 JST | clock-gate-2345 | started | coordinator | operate/work; vacancy leftover now not wait 23:59 |
| 2026-09-09 23:46:21 JST | leftover-reconstitute-2345a | started | worker-1 | 13704b file-vs-parent/sibling leftover; HOLD not PASS |
| 2026-09-09 23:46:21 JST | leftover-reconstitute-2345b | started | worker-2 | 7777 nested ancestor + 12083/13925 leftover; HOLD not PASS |
| 2026-09-09 23:46:21 JST | leftover-reconstitute-2345c | started | worker-3 | 14807 both-tables + 3062 tox.ini leftover; HOLD not PASS |
| 2026-09-09 23:46:28 JST | clock-gate-2345 | completed | coordinator | operate/work; occupy leftover now not wait 23:59 |
| 2026-09-09 23:46:28 JST | leftover-reconstitute-2345a | completed | worker-1 | 13913 collect-only 8.4.1 1 / pytest 9 unrecognized; HOLD no View |
| 2026-09-09 23:46:28 JST | leftover-reconstitute-2345b | completed | worker-2 | 14431 setup-show 1 pass all; HOLD no View |
| 2026-09-09 23:46:28 JST | leftover-reconstitute-2345c | completed | worker-3 | 14412 parent setup-show leftover name collision; HOLD no View |
| 2026-09-09 23:46:28 JST | contamination-2346 | completed | worker-1 | contamination clean |
| 2026-09-09 23:46:28 JST | no-collect-2346 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:46:28 JST | no-dream-2346 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:50:18 JST | clock-gate-2345 | completed | coordinator | operate/work; vacancy leftover now not wait 23:59 |
| 2026-09-09 23:50:18 JST | leftover-vacancy-2345a | completed | worker-1 | 13704b file-vs-parent 1 vs 3 keep-duplicates 4; file-vs-sibling n=2 all; HOLD no View |
| 2026-09-09 23:50:18 JST | leftover-vacancy-2345b | completed | worker-2 | 7777 nested ancestor 2 vs 5 keep-duplicates 7; mid-parent 2 vs 3; nested sibling n=3; 12083 same-subdir 1/2; 13925 '' '' ZeroDivision all; HOLD no View |
| 2026-09-09 23:50:18 JST | leftover-vacancy-2345c | completed | worker-3 | 14807 pytest.ini [pytest] wins; -c TOML native wins on 9 no UsageError; 3062 tox.ini raw getini InterpolationMissingOptionError; HOLD no View |
| 2026-09-09 23:50:18 JST | contamination-2347 | completed | worker-1 | contamination clean |
| 2026-09-09 23:50:18 JST | no-collect-2347 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-09 23:50:18 JST | no-dream-2347 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-09 23:54:57 JST | leftover-reconstitute-2353a | started | worker-1 | 14935 leftover extras basetemp/retention; HOLD not PASS |
| 2026-09-09 23:54:57 JST | leftover-reconstitute-2353b | started | worker-2 | 12083 leftover subdirectory vs cwd overlap; HOLD not PASS |
| 2026-09-09 23:54:57 JST | leftover-reconstitute-2353c | started | worker-3 | 14608c leftover collect-only/confcutdir/toml-addopts + 14807 leftover extra pairing; HOLD not PASS |
| 2026-09-10 00:01:26 JST | clock-gate-0000 | started | coordinator | operate/work; vacancy leftover now not wait 00:14 |
| 2026-09-10 00:01:26 JST | leftover-vacancy-0000a | started | worker-1 | 7777 deepest nested ancestor leftover; HOLD not PASS |
| 2026-09-10 00:01:26 JST | leftover-vacancy-0000b | started | worker-2 | 13704b file-in-parent + 13925 same-dot leftover; HOLD not PASS |
| 2026-09-10 00:01:26 JST | leftover-vacancy-0000c | started | worker-3 | 14964 keep-duplicates CASE1 + 3062 toml escaped leftover; HOLD not PASS |
| 2026-09-10 00:03:44 JST | leftover-reconstitute-2353a | completed | worker-1 | 14935 unique basetemp keeps from-a; shared overwrites; count=10 keeps; policy=all still last 3; HOLD no View |
| 2026-09-10 00:03:44 JST | leftover-reconstitute-2353b | completed | worker-2 | 12083 subdirectory vs cwd 1 vs 2 keep-duplicates 3; 13704 test_other vs parent 1 vs 2 keep-duplicates 3; HOLD no View |
| 2026-09-10 00:03:44 JST | leftover-reconstitute-2353c | completed | worker-3 | 14608c collect-only still 9.1.0 miss; pytest.toml/native list addopts rescue; 14807 setup.cfg both no Failed; HOLD no View |
| 2026-09-10 00:03:44 JST | leftover-reconstitute-0001a | started | worker-1 | 12083 three-way overlap leftover; HOLD not PASS |
| 2026-09-10 00:03:44 JST | leftover-reconstitute-0001b | started | worker-2 | 7777/13704b cwd-as-parent leftover; HOLD not PASS |
| 2026-09-10 00:03:44 JST | leftover-reconstitute-0001c | started | worker-3 | 13925 . . keep-duplicates + 14431 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:06:25 JST | clock-gate-0000 | completed | coordinator | operate/work; vacancy leftover now not wait 00:14 |
| 2026-09-10 00:06:25 JST | leftover-vacancy-0000a | completed | worker-1 | 7777 deepest a/b/c/d a/ 1 vs 5 keep-duplicates 6; mid 1 vs 3; vs Dir c 1 vs 2; sibling n=2; HOLD no View |
| 2026-09-10 00:06:25 JST | leftover-vacancy-0000b | completed | worker-2 | 13704b file-in-parent 1 vs 3 keep-duplicates 4; two files n=2; 13925 . . ZeroDivision keep-duplicates 2 errors; HOLD no View |
| 2026-09-10 00:06:25 JST | leftover-vacancy-0000c | completed | worker-3 | 14964 keep-duplicates CASE1 still 9.1.0 later miss collect-only n=3; 3062 pyproject %% literal; HOLD no View |
| 2026-09-10 00:06:25 JST | contamination-0000 | completed | worker-1 | contamination clean |
| 2026-09-10 00:06:25 JST | no-collect-0000 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 00:06:25 JST | no-dream-0000 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 00:06:37 JST | leftover-reconstitute-0001a | completed | worker-1 | 12083 three-way n=2 all (file hides 8/9); three dirs 1 vs 2 keep-duplicates 5; HOLD no View |
| 2026-09-10 00:06:37 JST | leftover-reconstitute-0001b | completed | worker-2 | 7777 a/b/c . same as a/b/c a/ 2 vs 5; 13704b a/b . same as a/b a/ 1 vs 3; HOLD no View |
| 2026-09-10 00:06:37 JST | leftover-reconstitute-0001c | completed | worker-3 | 13925 . . ZeroDivision all keep-duplicates 2 errors; 14431 collect-only default rc=5 / explicit 1; HOLD no View |
| 2026-09-10 00:07:10 JST | leftover-reconstitute-0006a | started | worker-1 | 14800 tb=short leftover; HOLD not PASS |
| 2026-09-10 00:07:10 JST | leftover-reconstitute-0006b | started | worker-2 | 14694 setup-show leftover; HOLD not PASS |
| 2026-09-10 00:07:10 JST | leftover-reconstitute-0006c | started | worker-3 | 13704 three-way leftover; HOLD not PASS |
| 2026-09-10 00:08:37 JST | leftover-reconstitute-0006a | completed | worker-1 | 14800 tb=short/plain still _finalizers from 9.1.0; 14101 tb=short still XPASS; HOLD no View |
| 2026-09-10 00:08:37 JST | leftover-reconstitute-0006b | completed | worker-2 | 14694 setup-show add_answer missing from 9.1.0 NameError; HOLD no View |
| 2026-09-10 00:08:37 JST | leftover-reconstitute-0006c | completed | worker-3 | 13704 three-way n=2 all; file+tests+. 1 vs 2; HOLD no View |
| 2026-09-10 00:08:57 JST | leftover-reconstitute-0008a | started | worker-1 | 14775 tb=short leftover; HOLD not PASS |
| 2026-09-10 00:08:57 JST | leftover-reconstitute-0008b | started | worker-2 | 14971/14640 collect-only gap leftover; HOLD not PASS |
| 2026-09-10 00:08:57 JST | leftover-reconstitute-0008c | started | worker-3 | 13885 tb=short leftover; HOLD not PASS |
| 2026-09-10 00:10:27 JST | leftover-reconstitute-0008a | completed | worker-1 | 14775 tb=short no-Werror 2 pass 1 warning from 9.1.0; -Werror 2 errors; HOLD no View |
| 2026-09-10 00:10:27 JST | leftover-reconstitute-0008b | completed | worker-2 | 14971/14640 collect-only gap n=3 all (miss is execute); HOLD no View |
| 2026-09-10 00:10:27 JST | leftover-reconstitute-0008c | completed | worker-3 | 13885 tb=short still autouse ERROR through 9.0.3 / skip from 9.1.0; HOLD no View |
| 2026-09-10 00:12:15 JST | leftover-reconstitute-0011a | started | worker-1 | 12083/13704/7777 file vs cwd leftover; HOLD not PASS |
| 2026-09-10 00:12:15 JST | leftover-reconstitute-0011b | started | worker-2 | 13965/13754/14431-family collect-only leftover; HOLD not PASS |
| 2026-09-10 00:12:15 JST | leftover-reconstitute-0011c | started | worker-3 | 14591/2043 tb=short leftover + 14808 setup-show; HOLD not PASS |
| 2026-09-10 00:14:57 JST | leftover-reconstitute-0011a | completed | worker-1 | 12083/13704/7777/13704b file-vs-cwd 8.4.1 drops cwd; HOLD no View |
| 2026-09-10 00:14:57 JST | leftover-reconstitute-0011b | completed | worker-2 | 13965 collect-only default rc=5 / test.py 1; 13754 collect-only 4 all; HOLD no View |
| 2026-09-10 00:14:57 JST | leftover-reconstitute-0011c | completed | worker-3 | 14591/2043 tb=short same collect split; 14808 setup-show surfaces getini; HOLD no View |
| 2026-09-10 00:14:57 JST | no-dream-0013 | completed | worker-1 | first live R1 already CHAIN-001/002/003 THIN_WRAPPER; no isomorphic 0004 |
| 2026-09-10 00:14:57 JST | leftover-reconstitute-0014a | started | worker-1 | 14011/5203/14095 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:14:57 JST | leftover-reconstitute-0014b | started | worker-2 | 13976/14650 tb=short leftover; HOLD not PASS |
| 2026-09-10 00:14:57 JST | leftover-reconstitute-0014c | started | worker-3 | 14051 setup-show + 14476 leftover; HOLD not PASS |
| 2026-09-10 00:16:46 JST | clock-gate-0015 | started | coordinator | operate/work; vacancy leftover now not wait 00:29 |
| 2026-09-10 00:16:46 JST | leftover-vacancy-0015a | started | worker-1 | 7777 nested file-vs-ancestor leftover; HOLD not PASS |
| 2026-09-10 00:16:46 JST | leftover-vacancy-0015b | started | worker-2 | 14964d keep-duplicates + 14964 setup-plan leftover; HOLD not PASS |
| 2026-09-10 00:16:46 JST | leftover-vacancy-0015c | started | worker-3 | 14737 tb=short + 3062 escaped live-log leftover; HOLD not PASS |
| 2026-09-10 00:16:54 JST | leftover-reconstitute-0014a | completed | worker-1 | 14011 collect-only 2 / tb=short still None; 5203/14095 collect-only 2 execute miss; HOLD no View |
| 2026-09-10 00:16:54 JST | leftover-reconstitute-0014b | completed | worker-2 | 13976 tb=short still 9.1.0 duplicate; 14650 tb=short 8.4.1 2 pass / pytest 9 duplicate IDs; HOLD no View |
| 2026-09-10 00:16:54 JST | leftover-reconstitute-0014c | completed | worker-3 | 14051 setup-show 1 pass; 14476 -k foo collect 2; HOLD no View |
| 2026-09-10 00:18:25 JST | leftover-reconstitute-0018a | started | worker-1 | 13784 collect-only + 14444 setup-show leftover; HOLD not PASS |
| 2026-09-10 00:18:25 JST | leftover-reconstitute-0018b | started | worker-2 | 14608 setup-show + 14148 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:18:25 JST | leftover-reconstitute-0018c | started | worker-3 | 14817 tb=short + 14448 setup-show leftover; HOLD not PASS |
| 2026-09-10 00:20:19 JST | leftover-reconstitute-0018a | completed | worker-1 | 13784 collect-only 1; 14444 setup-show 1 pass; HOLD no View |
| 2026-09-10 00:20:19 JST | leftover-reconstitute-0018b | completed | worker-2 | 14608 setup-show A B 2 pass; 14148 collect-only 1 even no:cacheprovider; 14613 setup-show 2 pass; HOLD no View |
| 2026-09-10 00:20:19 JST | leftover-reconstitute-0018c | completed | worker-3 | 14817 tb=short still bound-method; 14448/14815 setup-show no where; HOLD no View |
| 2026-09-10 00:20:28 JST | clock-gate-0015 | completed | coordinator | operate/work; vacancy leftover now not wait 00:29 |
| 2026-09-10 00:20:28 JST | leftover-vacancy-0015a | completed | worker-1 | 7777 nested file vs ancestor 1 vs 5 keep-duplicates 6; a/a vs cwd 1 vs 3; HOLD no View |
| 2026-09-10 00:20:28 JST | leftover-vacancy-0015b | completed | worker-2 | 14964 setup-plan miss at plan from 9.1.0; 14964d keep-duplicates still later miss collect-only n=3; HOLD no View |
| 2026-09-10 00:20:28 JST | leftover-vacancy-0015c | completed | worker-3 | 14737 tb=short still 1 fail; 3062 escaped live-log literal %(filename)s:3; HOLD no View |
| 2026-09-10 00:20:28 JST | contamination-0015 | completed | worker-1 | contamination clean |
| 2026-09-10 00:20:28 JST | no-collect-0015 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 00:20:28 JST | no-dream-0015 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 00:20:46 JST | leftover-reconstitute-0020a | started | worker-1 | 14816/14819/14820 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:20:46 JST | leftover-reconstitute-0020b | started | worker-2 | 14389 collect-only + 14445 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:20:46 JST | leftover-reconstitute-0020c | started | worker-3 | 14812 setup-show + 14973 tb=short leftover; HOLD not PASS |
| 2026-09-10 00:22:00 JST | leftover-reconstitute-0020a | completed | worker-1 | 14816/14819/14820 collect-only (miss is execute rewrite); HOLD no View |
| 2026-09-10 00:22:00 JST | leftover-reconstitute-0020b | completed | worker-2 | 14389/14445 collect-only (miss is execute); HOLD no View |
| 2026-09-10 00:22:00 JST | leftover-reconstitute-0020c | completed | worker-3 | 14812 setup-show still INTERNALERROR; 14973 tb=short still missing cleanup; 14702 tb=short 2 pass 1 skip; HOLD no View |
| 2026-09-10 00:22:14 JST | leftover-reconstitute-0022a | started | worker-1 | 11502/9298 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:22:14 JST | leftover-reconstitute-0022b | started | worker-2 | 13913/14811 setup-show leftover; HOLD not PASS |
| 2026-09-10 00:22:14 JST | leftover-reconstitute-0022c | started | worker-3 | 14255/14705 setup-show leftover; HOLD not PASS |
| 2026-09-10 00:23:45 JST | leftover-reconstitute-0022a | completed | worker-1 | 11502/9298 collect-only 1; HOLD no View |
| 2026-09-10 00:23:45 JST | leftover-reconstitute-0022b | completed | worker-2 | 13913 setup-show tests/ 1 pass; 14811 setup-show getini list fail; HOLD no View |
| 2026-09-10 00:23:45 JST | leftover-reconstitute-0022c | completed | worker-3 | 14255 quoted 1 pass / int native TypeError on 9; 14716 collect-only -c 1; 14514 setup-show no-args rc=5; HOLD no View |
| 2026-09-10 00:26:28 JST | leftover-reconstitute-0026a | started | worker-1 | 14514c/14514b leftover extras; HOLD not PASS |
| 2026-09-10 00:26:28 JST | leftover-reconstitute-0026b | started | worker-2 | 13699/14094 leftover extras; HOLD not PASS |
| 2026-09-10 00:26:28 JST | leftover-reconstitute-0026c | started | worker-3 | 14560/14488/14841 leftover extras; HOLD not PASS |
| 2026-09-10 00:30:33 JST | leftover-reconstitute-0026a | completed | worker-1 | 14514c/b setup-show importlib 1 pass; HOLD no View |
| 2026-09-10 00:30:33 JST | leftover-reconstitute-0026b | completed | worker-2 | 14094 collect-only 2; 14094b setup-show 2 fail 1 pass; 13699 setup-show still AttributeError; HOLD no View |
| 2026-09-10 00:30:33 JST | leftover-reconstitute-0026c | completed | worker-3 | 14488/14841/14691/13479/13885 collect-only (miss is execute); 14608c setup-show still 9.1.0 miss; HOLD no View |
| 2026-09-10 00:30:56 JST | leftover-reconstitute-0030a | started | worker-1 | 13985/14253/14092 setup-show leftover; HOLD not PASS |
| 2026-09-10 00:30:56 JST | leftover-reconstitute-0030b | started | worker-2 | 14705/14560 leftover extras; HOLD not PASS |
| 2026-09-10 00:30:56 JST | leftover-reconstitute-0030c | started | worker-3 | 14004/13755/9703 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:32:43 JST | clock-gate-0031 | started | coordinator | operate/work; vacancy leftover now not wait 00:44 |
| 2026-09-10 00:32:43 JST | leftover-vacancy-0031a | started | worker-1 | 14971/14640 setup-plan gap leftover; HOLD not PASS |
| 2026-09-10 00:32:43 JST | leftover-vacancy-0031b | started | worker-2 | 14964 setup-plan reverse + --lf leftover; HOLD not PASS |
| 2026-09-10 00:32:43 JST | leftover-vacancy-0031c | started | worker-3 | 7777 sibling nested file + 3062 full-escaped live-log leftover; HOLD not PASS |
| 2026-09-10 00:32:46 JST | leftover-reconstitute-0030a | completed | worker-1 | 13985 setup-show string TypeError on 9 / list+ini_options 1 pass; 14253/14092 ini_options 1 pass; HOLD no View |
| 2026-09-10 00:32:46 JST | leftover-reconstitute-0030b | completed | worker-2 | 14705 setup-show -c tool 8 unread / 9 bench; 14560 collect-only KeyError; HOLD no View |
| 2026-09-10 00:32:46 JST | leftover-reconstitute-0030c | completed | worker-3 | 14004 collect-only 4; 13755 collect-only 22; 9703 collect-only collapsed nodeids; HOLD no View |
| 2026-09-10 00:34:10 JST | leftover-reconstitute-0033a | started | worker-1 | 14412/14696 leftover extras; HOLD not PASS |
| 2026-09-10 00:34:10 JST | leftover-reconstitute-0033b | started | worker-2 | 14048/13965 leftover extras; HOLD not PASS |
| 2026-09-10 00:34:10 JST | leftover-reconstitute-0033c | started | worker-3 | 14004b/13755b/9703b leftover extras; HOLD not PASS |
| 2026-09-10 00:36:58 JST | clock-gate-0031 | completed | coordinator | operate/work; vacancy leftover now not wait 00:44 |
| 2026-09-10 00:36:58 JST | leftover-vacancy-0031a | completed | worker-1 | 14971/14640 setup-plan gap later ERROR from 9.1.0; no-gap OK; HOLD no View |
| 2026-09-10 00:36:58 JST | leftover-vacancy-0031b | completed | worker-2 | 14964 --lf 8.4.1 both errors / 9.1.0 only test_a; reverse plan later without guard; HOLD no View |
| 2026-09-10 00:36:58 JST | leftover-vacancy-0031c | completed | worker-3 | 7777 nested file vs sibling n=2; 3062 full-escaped live-log ValueError %W; HOLD no View |
| 2026-09-10 00:36:58 JST | contamination-0031 | completed | worker-1 | contamination clean |
| 2026-09-10 00:36:58 JST | no-collect-0031 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 00:36:58 JST | no-dream-0031 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 00:41:52 JST | clock-gate-0041 | started | coordinator | operate/work; vacancy leftover now not wait 00:44 |
| 2026-09-10 00:41:52 JST | leftover-vacancy-0041a | started | worker-1 | 14971/14640 --lf/--ff after gap leftover; HOLD not PASS |
| 2026-09-10 00:41:52 JST | leftover-vacancy-0041b | started | worker-2 | 14964 --ff/--lfnf/--maxfail leftover; HOLD not PASS |
| 2026-09-10 00:41:52 JST | leftover-vacancy-0041c | started | worker-3 | 7777 file-vs-own-dir + 13704b file-vs-own-dir + 14807 ini+toml leftover; HOLD not PASS |
| 2026-09-10 00:44:20 JST | leftover-reconstitute-0033a | completed | worker-1 | 14412 alt collect-only 1 UnitTestCase all; 14696 iso_miss existing+missing 9.1.0-only unrecognized; HOLD no View |
| 2026-09-10 00:44:20 JST | leftover-reconstitute-0033b | completed | worker-2 | 14048 setup-show --pyargs no PYTHONPATH rc=4 / PYTHONPATH=. 1 pass; 13965 setup-show 1 pass pytest9 1000 subtests; HOLD no View |
| 2026-09-10 00:44:20 JST | leftover-reconstitute-0033c | completed | worker-3 | 14004b collect-only from sdk/ 3 all; 13755b collect-only 4; 9703b collect-only 2 ::test_same; HOLD no View |
| 2026-09-10 00:44:20 JST | leftover-reconstitute-0033d | completed | worker-1 | 14800/14101/14775/13882/14683/14700/14635/14323 collect-only (miss is execute); HOLD no View |
| 2026-09-10 00:44:20 JST | leftover-reconstitute-0039a | started | worker-1 | 14640/14971/14964d --lf after gap leftover; HOLD not PASS |
| 2026-09-10 00:44:20 JST | leftover-reconstitute-0039b | started | worker-2 | 14004b/9703/13755/14104 setup-plan + 7777b file-vs-cwd leftover; HOLD not PASS |
| 2026-09-10 00:44:20 JST | leftover-reconstitute-0039c | started | worker-3 | 14694/14812/14973/14702/13246/14814 collect-only + 13699 tb=short PYTHONPATH + 14696 iso_miss setup-show; HOLD not PASS |
| 2026-09-10 00:46:26 JST | clock-gate-0041 | completed | coordinator | operate/work; vacancy leftover now not wait 00:44/00:59 |
| 2026-09-10 00:46:26 JST | leftover-vacancy-0041a | completed | worker-1 | 14971/14640 --lf later ERROR last-failed from 9.1.0; --ff still later miss; HOLD no View |
| 2026-09-10 00:46:26 JST | leftover-vacancy-0041b | completed | worker-2 | 14964 --ff still later PASS; --maxfail=1 hides later miss; 14964d --lf same as 14964; HOLD no View |
| 2026-09-10 00:46:26 JST | leftover-vacancy-0041c | completed | worker-3 | 7777/13704b file vs containing dir n=1 all keep 2; 14807 ini+toml 8.4.1 ini / pytest 9 toml; HOLD no View |
| 2026-09-10 00:46:26 JST | contamination-0041 | completed | worker-1 | contamination clean |
| 2026-09-10 00:46:26 JST | no-collect-0041 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 00:46:26 JST | no-dream-0041 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 00:50:20 JST | leftover-reconstitute-0039a | completed | worker-1 | 14640/14971 --lf later ERROR last-failed then 1 pass (gap skipped); 14964d --lf same as 14964; HOLD no View |
| 2026-09-10 00:50:20 JST | leftover-reconstitute-0039b | completed | worker-2 | 14004b/9703 setup-plan leak visible through 9.0.3; 13755 plan 10S/10T; 14104 session carry at plan; 7777b file-vs-cwd 1 vs 3 keep 4; HOLD no View |
| 2026-09-10 00:50:20 JST | leftover-reconstitute-0039c | completed | worker-3 | 14694/14812/14973/14702/13246/14814 collect-only miss is execute; 13699 tb=short still AttributeError; 14696 iso_miss existing unrecognized all / missing 9.1.0-only; HOLD no View |
| 2026-09-10 00:50:20 JST | leftover-reconstitute-0048a | started | worker-1 | 13976/14591/2043/14650 setup-plan leftover; HOLD not PASS |
| 2026-09-10 00:50:20 JST | leftover-reconstitute-0048b | started | worker-2 | 14148 cache-show/clear; 14613 cache-show; 14608c --override-ini addopts leftover; HOLD not PASS |
| 2026-09-10 00:50:20 JST | leftover-reconstitute-0048c | started | worker-3 | 14412 durations; 13784 tb=short -s; 14817 setup-show; 14800/14775 --lf leftover; HOLD not PASS |
| 2026-09-10 00:52:33 JST | leftover-reconstitute-0048a | completed | worker-1 | 13976/14591/2043 setup-plan same collect split; 14650 plan pytest9 duplicate IDs; HOLD no View |
| 2026-09-10 00:52:33 JST | leftover-reconstitute-0048b | completed | worker-2 | 14148 --cache-show nodeids / no:cacheprovider unrecognized; 14608c --override-ini addopts=tests rescues 9.1.0 on alt_inside; HOLD no View |
| 2026-09-10 00:52:33 JST | leftover-reconstitute-0048c | completed | worker-3 | 14412 durations not per-subtest us; 13784 tb=short still doubling; 14800 --lf hides _finalizers; 14775 --lf still 2 errors; HOLD no View |
| 2026-09-10 00:54:09 JST | leftover-reconstitute-0052a | started | worker-1 | 12083/13704/7777 setup-plan overlap leftover; HOLD not PASS |
| 2026-09-10 00:54:09 JST | leftover-reconstitute-0052b | started | worker-2 | 13925/14444/14762/13922/14877 leftover extras; HOLD not PASS |
| 2026-09-10 00:54:09 JST | leftover-reconstitute-0052c | started | worker-3 | 13885 --lf after skip vs fire leftover; HOLD not PASS |
| 2026-09-10 00:55:58 JST | leftover-reconstitute-0052a | completed | worker-1 | 12083/13704/7777 setup-plan same overlap drop as collect; HOLD no View |
| 2026-09-10 00:55:58 JST | leftover-reconstitute-0052b | completed | worker-2 | 13925 setup-plan empty 8.4.1 drops cwd / pytest9 ZeroDivision; 14444 plan hides capture; 14762 setup-show 1 pass; 13922 extra rc=4; HOLD no View |
| 2026-09-10 00:55:58 JST | leftover-reconstitute-0052c | completed | worker-3 | 13885 --lf 8.4.1-9.0.3 still ERROR / 9.1.0 skip no last-failed; HOLD no View |
| 2026-09-10 00:56:14 JST | leftover-reconstitute-0056a | started | worker-1 | 5203/14095/14011 setup-plan leftover; HOLD not PASS |
| 2026-09-10 00:56:14 JST | leftover-reconstitute-0056b | started | worker-2 | 14691/14444 collect-only leftover; HOLD not PASS |
| 2026-09-10 00:56:14 JST | leftover-reconstitute-0056c | started | worker-3 | 14877 python count.py leftover already; 13479 setup-plan leftover; HOLD not PASS |
| 2026-09-10 00:57:18 JST | leftover-reconstitute-0056a | completed | worker-1 | 5203/14095 setup-plan b from first a; 14011 setup-plan class fix per subclass; HOLD no View |
| 2026-09-10 00:57:18 JST | leftover-reconstitute-0056b | completed | worker-2 | 14691 setup-plan sample not found; 14444 collect-only 2; HOLD no View |
| 2026-09-10 00:57:18 JST | leftover-reconstitute-0056c | completed | worker-3 | 13479 setup-plan ff not found at plan; HOLD no View |
| 2026-09-10 00:59:21 JST | leftover-reconstitute-0059a | started | worker-1 | 12083/13704b/7777b setup-plan reverse/keep leftover; HOLD not PASS |
| 2026-09-10 00:59:21 JST | leftover-reconstitute-0059b | started | worker-2 | 14800/14775/13885 --ff + 14101 --lf leftover; HOLD not PASS |
| 2026-09-10 00:59:21 JST | leftover-reconstitute-0059c | started | worker-3 | 14613 cache-show after run; 14148 nocache --cache-clear; 14650b/c plan; 14608c override-ini correct db-url; HOLD not PASS |
| 2026-09-10 01:00:58 JST | leftover-reconstitute-0059a | completed | worker-1 | 12083 reverse plan 1 vs 2 keep 3; 13704b plan 1 vs 3 keep 4; 7777b plan 1 vs 3; HOLD no View |
| 2026-09-10 01:00:58 JST | leftover-reconstitute-0059b | completed | worker-2 | 14800 --ff hides _finalizers (2 pass 1 skip); 14775 --ff still 2 errors; 13885 --ff still 8/9 split; 14101 --lf XPASS not last-failed; HOLD no View |
| 2026-09-10 01:00:58 JST | leftover-reconstitute-0059c | completed | worker-3 | 14613 cache-show after run has nodeids; 14148 nocache --cache-clear unrecognized; 14650b plan 2 all; 14650c plan pytest9 duplicate; 14608c override-ini 1 pass including 9.1.0; HOLD no View |
| 2026-09-10 01:01:54 JST | leftover-reconstitute-0101a | started | worker-1 | 13704/7777 reverse/keep setup-plan; 13925 dot-parent plan leftover; HOLD not PASS |
| 2026-09-10 01:01:55 JST | leftover-reconstitute-0101b | started | worker-2 | 14101 --ff; 13784 --assert=plain -s; 14389 --tb=line leftover; HOLD not PASS |
| 2026-09-10 01:01:55 JST | leftover-reconstitute-0101c | started | worker-3 | 13699 --assert=plain PYTHONPATH; 14808/14448/14255 tb leftover; HOLD not PASS |
| 2026-09-10 01:02:26 JST | clock-gate-0101 | started | coordinator | operate/work; vacancy leftover now not wait 01:14 |
| 2026-09-10 01:02:26 JST | leftover-vacancy-0101a | started | worker-1 | 14807 dual-file ini+pyproject/toml leftover; HOLD not PASS |
| 2026-09-10 01:02:26 JST | leftover-vacancy-0101b | started | worker-2 | 14964 --nf + 14971/14640 --maxfail=1 leftover; HOLD not PASS |
| 2026-09-10 01:02:26 JST | leftover-vacancy-0101c | started | worker-3 | 14737 --lf leftover; HOLD not PASS |
| 2026-09-10 01:03:14 JST | leftover-reconstitute-0101a | completed | worker-1 | 13704 reverse plan 1 vs 2 keep 3; 7777 reverse 3 vs 5 keep 8; 13925 . a/ 8.4.1 drop cwd / pytest9 ZeroDivision; HOLD no View |
| 2026-09-10 01:03:14 JST | leftover-reconstitute-0101b | completed | worker-2 | 14101 --ff still XPASS; 13784 plain -s still doubling; 14389 --tb=line During handling gone 8.4.1 and 9.1.0+; HOLD no View |
| 2026-09-10 01:03:14 JST | leftover-reconstitute-0101c | completed | worker-3 | 13699 plain still AttributeError; 14808 tb=short still list isinstance; 14448 tb=native no where; 14255 int_native tb=short TypeError on 9; HOLD no View |
| 2026-09-10 01:04:11 JST | leftover-reconstitute-0103a | started | worker-1 | 13704 same-file plan; 12083 subdir vs cwd plan; 7777 file-vs-cwd plan leftover; HOLD not PASS |
| 2026-09-10 01:04:11 JST | leftover-reconstitute-0103b | started | worker-2 | 14811/14716/14514c/14431 tb=short leftover; HOLD not PASS |
| 2026-09-10 01:04:11 JST | leftover-reconstitute-0103c | started | worker-3 | 14694 tb=short doctest; 14841 setup-show; 13913 tb=short; 11502 tb=short leftover; HOLD not PASS |
| 2026-09-10 01:04:32 JST | clock-gate-0101 | completed | coordinator | operate/work; vacancy leftover now not wait 01:14 |
| 2026-09-10 01:04:32 JST | leftover-vacancy-0101a | completed | worker-1 | 14807 pytest.ini beats pyproject all; named toml beats setup.cfg from 9.0.1; HOLD no View |
| 2026-09-10 01:04:32 JST | leftover-vacancy-0101b | completed | worker-2 | 14964 --nf later miss visible; 14971/14640 --maxfail=1 later miss visible; HOLD no View |
| 2026-09-10 01:04:32 JST | leftover-vacancy-0101c | completed | worker-3 | 14737 --lf still 1 fail; HOLD no View |
| 2026-09-10 01:04:32 JST | contamination-0101 | completed | worker-1 | contamination clean |
| 2026-09-10 01:04:32 JST | no-collect-0101 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 01:04:32 JST | no-dream-0101 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 01:06:06 JST | leftover-reconstitute-0103a | completed | worker-1 | 13704 same-file plan 2 vs 1; 12083 subdir vs cwd plan 1 vs 2; 7777 file-vs-cwd plan 1 vs 5; HOLD no View |
| 2026-09-10 01:06:06 JST | leftover-reconstitute-0103b | completed | worker-2 | 14811/14716/14514c/14431 tb=short 1 pass; HOLD no View |
| 2026-09-10 01:06:06 JST | leftover-reconstitute-0103c | completed | worker-3 | 14694 tb=short NameError from 9.1.0; 14841 setup-show still resource_tracker; 13913 tb=short tests/ 1 pass; 11502 tb=short 1 pass; HOLD no View |
| 2026-09-10 01:06:43 JST | leftover-reconstitute-0106a | started | worker-1 | 13704b file-vs-cwd plan; 12083 keep subdir cwd plan leftover; HOLD not PASS |
| 2026-09-10 01:06:43 JST | leftover-reconstitute-0106b | started | worker-2 | 9298/3062/14004 leftover extras; HOLD not PASS |
| 2026-09-10 01:06:43 JST | leftover-reconstitute-0106c | started | worker-3 | 13913 tb=short no path leftover; HOLD not PASS |
| 2026-09-10 01:07:30 JST | leftover-reconstitute-0106a | completed | worker-1 | 13704b file-vs-cwd plan 1 vs 3; 12083 keep subdir cwd plan n=3 all; HOLD no View |
| 2026-09-10 01:07:30 JST | leftover-reconstitute-0106b | completed | worker-2 | 9298 tb=short 1 pass; 14004 setup-plan 4 no leak; HOLD no View |
| 2026-09-10 01:07:30 JST | leftover-reconstitute-0106c | completed | worker-3 | 13913 tb=short no path 8.4.1 pass / pytest9 unrecognized; HOLD no View |
| 2026-09-10 01:07:51 JST | leftover-reconstitute-0108a | started | worker-1 | 13925 keep-duplicates . a/ setup-plan leftover; HOLD not PASS |
| 2026-09-10 01:07:51 JST | leftover-reconstitute-0108b | started | worker-2 | 7777b keep-duplicates setup-plan leftover; HOLD not PASS |
| 2026-09-10 01:07:51 JST | leftover-reconstitute-0108c | started | worker-3 | 3062 --tb=short leftover; HOLD not PASS |
| 2026-09-10 01:08:25 JST | leftover-reconstitute-0108a | completed | worker-1 | 13925 keep-duplicates . a/ plan ZeroDivision on 8.4.1 too; HOLD no View |
| 2026-09-10 01:08:25 JST | leftover-reconstitute-0108b | completed | worker-2 | 7777b keep-duplicates setup-plan n=4 all; HOLD no View |
| 2026-09-10 01:08:26 JST | leftover-reconstitute-0108c | completed | worker-3 | 3062 tb=short parent tree leftover layout collisions; HOLD no View |
| 2026-09-10 01:11:35 JST | leftover-reconstitute-0111a | started | worker-1 | 13704/12083/7777/13925 same-dir twice setup-plan leftover; HOLD not PASS |
| 2026-09-10 01:11:35 JST | leftover-reconstitute-0111b | started | worker-2 | 14800/14775 --maxfail=1; 14964d --ff leftover; HOLD not PASS |
| 2026-09-10 01:11:35 JST | leftover-reconstitute-0111c | started | worker-3 | 14476/14271/13246/14814/3062 leftover extras; HOLD not PASS |
| 2026-09-10 01:13:18 JST | leftover-reconstitute-0111a | completed | worker-1 | same-dir twice setup-plan unique 2/2/5/1 keep 4/4; HOLD no View |
| 2026-09-10 01:13:18 JST | leftover-reconstitute-0111b | completed | worker-2 | 14800/14775 --maxfail=1 hides second error from 9.1.0; 14964d --ff later also ERROR; HOLD no View |
| 2026-09-10 01:13:18 JST | leftover-reconstitute-0111c | completed | worker-3 | 14476 setup-show -k foo 2 pass; 14271 setup-show 1 pass; 13246 tb=short still shadow; 14814 setup-show still starred; 3062 cfg-getini tb=short 1 pass; HOLD no View |
| 2026-09-10 01:14:03 JST | leftover-reconstitute-0114a | started | worker-1 | 14591/13976/2043 --lf after collect-error leftover; HOLD not PASS |
| 2026-09-10 01:14:03 JST | leftover-reconstitute-0114b | started | worker-2 | 13885/14101 --maxfail=1; 14817 --assert=plain leftover; HOLD not PASS |
| 2026-09-10 01:14:03 JST | leftover-reconstitute-0114c | started | worker-3 | 14608c --noconftest; 14650 --lf; 14444 --capture=sys leftover; HOLD not PASS |
| 2026-09-10 01:15:13 JST | leftover-reconstitute-0114a | completed | worker-1 | 14591/13976/2043 --lf collect-error is not last-failed; HOLD no View |
| 2026-09-10 01:15:13 JST | leftover-reconstitute-0114b | completed | worker-2 | 13885 --maxfail=1 still 8/9 split; 14101 --maxfail=1 still XPASS; 14817 --assert=plain no where; HOLD no View |
| 2026-09-10 01:15:13 JST | leftover-reconstitute-0114c | completed | worker-3 | 14608c --noconftest unrecognized all; 14444 --capture=sys 2 pass; 14650 --lf collect-error not last-failed; HOLD no View |
| 2026-09-10 01:16:15 JST | leftover-reconstitute-0116a | started | worker-1 | 7777 keep-duplicates same-dir plan; 13925 keep a/ a/ plan leftover; HOLD not PASS |
| 2026-09-10 01:16:15 JST | leftover-reconstitute-0116b | started | worker-2 | 14800 --nf leftover; HOLD not PASS |
| 2026-09-10 01:16:15 JST | leftover-reconstitute-0116c | started | worker-3 | 9703 --lf leftover; HOLD not PASS |
| 2026-09-10 01:17:00 JST | clock-gate-0115 | started | coordinator | operate/work; vacancy leftover now not wait 01:29 |
| 2026-09-10 01:17:00 JST | leftover-vacancy-0115a | started | worker-1 | 14807 toml/pyproject dual-file leftover; HOLD not PASS |
| 2026-09-10 01:17:00 JST | leftover-vacancy-0115b | started | worker-2 | 14964 --sw leftover; HOLD not PASS |
| 2026-09-10 01:17:00 JST | leftover-vacancy-0115c | started | worker-3 | 14971/14640 --nf leftover; HOLD not PASS |
| 2026-09-10 01:17:05 JST | leftover-reconstitute-0116a | completed | worker-1 | 7777 keep-duplicates same-dir plan n=10; 13925 keep a/ a/ plan n=2; HOLD no View |
| 2026-09-10 01:17:05 JST | leftover-reconstitute-0116b | completed | worker-2 | 14800 --nf still 2 _finalizers errors (does not hide); HOLD no View |
| 2026-09-10 01:17:05 JST | leftover-reconstitute-0116c | completed | worker-3 | 9703 --lf 2 pass no last-failed; HOLD no View |
| 2026-09-10 01:18:57 JST | clock-gate-0115 | completed | coordinator | operate/work; vacancy leftover now not wait 01:29 |
| 2026-09-10 01:18:57 JST | leftover-vacancy-0115a | completed | worker-1 | 14807 ini+pyboth UsageError on 9; toml beats pyproject; scfg loses to native on 9; HOLD no View |
| 2026-09-10 01:18:57 JST | leftover-vacancy-0115b | completed | worker-2 | 14964 --sw stuck on first error hides later miss; HOLD no View |
| 2026-09-10 01:18:57 JST | leftover-vacancy-0115c | completed | worker-3 | 14971/14640 --nf later miss still visible; HOLD no View |
| 2026-09-10 01:18:57 JST | contamination-0115 | completed | worker-1 | contamination clean |
| 2026-09-10 01:18:57 JST | no-collect-0115 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 01:18:57 JST | no-dream-0115 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 01:19:39 JST | leftover-reconstitute-0119a | started | worker-1 | 14775/13885/14101 --nf leftover; HOLD not PASS |
| 2026-09-10 01:19:39 JST | leftover-reconstitute-0119b | started | worker-2 | 14964d --maxfail=1; 14591/2043 --ff leftover; HOLD not PASS |
| 2026-09-10 01:19:39 JST | leftover-reconstitute-0119c | started | worker-3 | 14815/14816 plain; 14476 tb -k foo; 7777b reverse plan; 12083 subdir vs parent plan; 14271 showmp leftover; HOLD not PASS |
| 2026-09-10 01:21:07 JST | leftover-reconstitute-0119a | completed | worker-1 | 14775 --nf -Werror still 2 errors; 13885 --nf still 8/9; 14101 --nf still XPASS; HOLD no View |
| 2026-09-10 01:21:07 JST | leftover-reconstitute-0119b | completed | worker-2 | 14964d --maxfail=1 1 error all (hides later); 14591/2043 --ff collect-error not last-failed; HOLD no View |
| 2026-09-10 01:21:07 JST | leftover-reconstitute-0119c | completed | worker-3 | 14815/14816 --assert=plain no where; 7777b reverse plan 1 vs 3; 12083 subdir vs parent plan 1 vs 2; HOLD no View |
| 2026-09-10 01:22:03 JST | leftover-reconstitute-0122a | started | worker-1 | 14814 --assert=plain; 14444 with_hook --capture=sys leftover; HOLD not PASS |
| 2026-09-10 01:22:03 JST | leftover-reconstitute-0122b | started | worker-2 | 14650 --ff; 14148 cache-show after run leftover; HOLD not PASS |
| 2026-09-10 01:22:03 JST | leftover-reconstitute-0122c | started | worker-3 | 13246 --setup-plan; 9703 --ff leftover; HOLD not PASS |
| 2026-09-10 01:22:45 JST | leftover-reconstitute-0122a | completed | worker-1 | 14814 --assert=plain 3 pass; 14444 with_hook --capture=sys 2 pass; HOLD no View |
| 2026-09-10 01:22:45 JST | leftover-reconstitute-0122b | completed | worker-2 | 14650 --ff collect-error not last-failed; 14148 cache-show after run has nodeids; HOLD no View |
| 2026-09-10 01:22:45 JST | leftover-reconstitute-0122c | completed | worker-3 | 13246 setup-plan lists both value; 9703 --ff 2 pass no last-failed; HOLD no View |
| 2026-09-10 01:26:58 JST | leftover-reconstitute-0126a | started | worker-1 | 13704b keep same-dir plan; 7777 a/b2 a/ plan; 12083 keep subdir vs parent plan leftover; HOLD not PASS |
| 2026-09-10 01:26:58 JST | leftover-reconstitute-0126b | started | worker-2 | 14800/14775 --sw; 14964d --nf leftover; HOLD not PASS |
| 2026-09-10 01:26:58 JST | leftover-reconstitute-0126c | started | worker-3 | 13699 --tb=line; 14514c default tb; 13913 setup-plan; 3062/14808/14762 tb leftover; HOLD not PASS |
| 2026-09-10 01:28:32 JST | leftover-reconstitute-0126a | completed | worker-1 | 13704b keep same-dir plan n=6; 7777 a/b2 a/ plan 1 vs 5; 12083 keep subdir vs parent plan n=3; HOLD no View |
| 2026-09-10 01:28:32 JST | leftover-reconstitute-0126b | completed | worker-2 | 14800 --sw hides _finalizers (2nd run 2 pass); 14775 --sw hides second _finalizers; 14964d --nf later also ERROR; HOLD no View |
| 2026-09-10 01:28:32 JST | leftover-reconstitute-0126c | completed | worker-3 | 13699 --tb=line still AttributeError; 14514c default tb ImportError; 13913 plan tests/ 1; 14808 tool tb TypeError on 9; HOLD no View |
| 2026-09-10 01:28:32 JST | leftover-reconstitute-0129a | started | worker-1 | 13704b same-dir plan; 7777b a/b2 a/ plan; 13925 -- a/ plan leftover; HOLD not PASS |
| 2026-09-10 01:28:32 JST | leftover-reconstitute-0129b | started | worker-2 | 13885/14101 --sw; 13913 no-path setup-plan leftover; HOLD not PASS |
| 2026-09-10 01:28:32 JST | leftover-reconstitute-0129c | started | worker-3 | 14808 pytest_ini tb; 11502 setup-plan; 14650b --lf leftover; HOLD not PASS |
| 2026-09-10 01:31:18 JST | clock-gate-0130 | started | coordinator | operate/work; vacancy leftover now not wait 01:44 |
| 2026-09-10 01:31:18 JST | leftover-vacancy-0130a | started | worker-1 | 14807 tox+pyproject / -c toml leftover; HOLD not PASS |
| 2026-09-10 01:31:18 JST | leftover-vacancy-0130b | started | worker-2 | 14971 --sw leftover; HOLD not PASS |
| 2026-09-10 01:31:18 JST | leftover-vacancy-0130c | started | worker-3 | 14640 --sw leftover; HOLD not PASS |
| 2026-09-10 01:32:58 JST | clock-gate-0130 | completed | coordinator | operate/work; vacancy leftover now not wait 01:44 |
| 2026-09-10 01:32:58 JST | leftover-vacancy-0130a | completed | worker-1 | 14807 tox+pyproject native 8.4.1 tox / 9 native; -c toml displaces ini; HOLD no View |
| 2026-09-10 01:32:58 JST | leftover-vacancy-0130b | completed | worker-2 | 14971 --sw later miss visible then stuck on later ERROR; HOLD no View |
| 2026-09-10 01:32:58 JST | leftover-vacancy-0130c | completed | worker-3 | 14640 --sw later miss visible then stuck on later ERROR; HOLD no View |
| 2026-09-10 01:32:58 JST | contamination-0130 | completed | worker-1 | contamination clean |
| 2026-09-10 01:32:58 JST | no-collect-0130 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 01:32:58 JST | no-dream-0130 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0126a | completed | worker-1 | 13704b keep same-dir plan n=6; 7777 a/b2 a/ plan 1 vs 5; 12083 keep subdir vs parent plan n=3; HOLD no View |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0126b | completed | worker-2 | 14800 --sw hides _finalizers (2nd run 2 pass); 14775 --sw hides second _finalizers; 14964d --nf later also ERROR; HOLD no View |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0126c | completed | worker-3 | 13699 --tb=line still AttributeError; 14514c default tb ImportError; 13913 plan tests/ 1; 14808 tool tb TypeError on 9; HOLD no View |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0129a | completed | worker-1 | 13704b same-dir plan n=3 all; 7777b a/b2 a/ plan 1 vs 3; 13925 -- a/ plan n=1 all; HOLD no View |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0129b | completed | worker-2 | 13885 --sw still 8/9; 14101 --sw XPASS not stepwise-failed; 13913 no-path plan 8.4.1 1 / pytest9 unrecognized; HOLD no View |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0129c | completed | worker-3 | 14808 pytest_ini tb 1 pass all; 11502 setup-plan 1 collected all; 14650b --lf 2 pass no last-failed; HOLD no View |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0131a | started | worker-1 | 7777b keep a/b2 plan; 13925 keep -- a/ plan; 12083/13704 three-way plan leftover; HOLD not PASS |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0131b | started | worker-2 | 14964d --sw; 14737 --ff/--sw; 14004b --lf; 13755b --lf; 9703 --nf leftover; HOLD not PASS |
| 2026-09-10 01:36:29 JST | leftover-reconstitute-0131c | started | worker-3 | 14808 pytest_ini plan; 13784 --tb=line; 14650c --lf; 13754/13965/14514c/14431 plan; 14812 plain leftover; HOLD not PASS |
| 2026-09-10 01:40:10 JST | leftover-reconstitute-0131a | completed | worker-1 | 7777b keep a/b2 plan n=4; 13925 keep -- a/ n=1; 12083 three-way plan n=2 all; 13704 three-way plan 1 vs 2; HOLD no View |
| 2026-09-10 01:40:10 JST | leftover-reconstitute-0131b | completed | worker-2 | 14964d --sw hides later miss; 14737 --ff/--sw still 1 fail; 14004b --lf 3 pass; 13755b --lf hides session miss (2 pass); 9703 --nf 2 pass; HOLD no View |
| 2026-09-10 01:40:10 JST | leftover-reconstitute-0131c | completed | worker-3 | 14808 pytest_ini plan 1; 13784 --tb=line still doubling through 9.0.3; 14650c --lf collect-error not last-failed; 13754/13965/14431 plan; 14514c plan ImportError; 14812 plain INTERNALERROR; HOLD no View |
| 2026-09-10 01:40:10 JST | leftover-reconstitute-0134a | started | worker-1 | 7777 keep a/b2 plan; 12083/13704 keep three-way plan leftover; HOLD not PASS |
| 2026-09-10 01:40:10 JST | leftover-reconstitute-0134b | started | worker-2 | 13755b --ff/--sw/--nf; 14650c --ff; 9703b --ff; 13479 --lf leftover; HOLD not PASS |
| 2026-09-10 01:40:10 JST | leftover-reconstitute-0134c | started | worker-3 | 14514c importlib plan; 9298/14716/14811/14412/14048 plan; 14819 --tb=line; 13913 nopath --lf leftover; HOLD not PASS |
| 2026-09-10 01:44:25 JST | leftover-reconstitute-0134a | completed | worker-1 | 7777 keep a/b2 plan n=6; 12083 keep three-way plan n=4; 13704 keep three-way plan n=5; HOLD no View |
| 2026-09-10 01:44:25 JST | leftover-reconstitute-0134b | completed | worker-2 | 13755b --ff swaps miss onto test_a; --sw hides remaining; --nf still 2 errors; 14650c --ff collect-error not last-failed; 9703b --ff 2 pass; 13479 --lf still ff missing; HOLD no View |
| 2026-09-10 01:44:25 JST | leftover-reconstitute-0134c | completed | worker-3 | 14514c importlib plan 1; 9298/14716/14811/14412/14048 plan 1; 14819 --tb=line still 2 fail; 13913 nopath --lf 8.4.1 pass / pytest9 unrecognized; HOLD no View |
| 2026-09-10 01:44:25 JST | leftover-reconstitute-0137a | started | worker-1 | 13755b --maxfail=1 leftover; HOLD not PASS |
| 2026-09-10 01:44:25 JST | leftover-reconstitute-0137b | started | worker-2 | 14011/14691/5203/14095/14811 --lf leftover; HOLD not PASS |
| 2026-09-10 01:44:25 JST | leftover-reconstitute-0137c | started | worker-3 | 14820/14445 --tb=line; 14255/3062/14716/14048 plan leftover; HOLD not PASS |
| 2026-09-10 01:46:00 JST | leftover-reconstitute-0137a | completed | worker-1 | 13755b --maxfail=1 2 pass 1 error (hides second test_b); HOLD no View |
| 2026-09-10 01:46:00 JST | leftover-reconstitute-0137b | completed | worker-2 | 14011 --lf still 2 fail; 14691 --lf still sample missing; 5203/14095 --lf hides rebuild miss (1 pass); 14811 --lf still getini fail; HOLD no View |
| 2026-09-10 01:46:00 JST | leftover-reconstitute-0137c | completed | worker-3 | 14820/14445 --tb=line still rewrite miss; 14255 quoted plan 1 / int_native TypeError on 9; 3062 plan 1; 14716 missing toml FileNotFoundError; 14048 --pyargs plan 1; HOLD no View |
| 2026-09-10 01:46:00 JST | leftover-reconstitute-0140a | started | worker-1 | 5203 --ff/--nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 01:46:00 JST | leftover-reconstitute-0140b | started | worker-2 | 14095 --ff/--nf/--sw/--maxfail; 14011/14691 --ff leftover; HOLD not PASS |
| 2026-09-10 01:46:00 JST | leftover-reconstitute-0140c | started | worker-3 | 13246/14104 --lf leftover; HOLD not PASS |
| 2026-09-10 01:46:24 JST | clock-gate-0145 | started | coordinator | operate/work; vacancy leftover now not wait 01:59 |
| 2026-09-10 01:46:24 JST | leftover-vacancy-0145a | started | worker-1 | 14807 -c custom.ini vs pyproject leftover; HOLD not PASS |
| 2026-09-10 01:46:24 JST | leftover-vacancy-0145b | started | worker-2 | 14807 -c custom.ini vs pytest.toml/ini leftover; HOLD not PASS |
| 2026-09-10 01:46:24 JST | leftover-vacancy-0145c | started | worker-3 | 14807 -c toml vs named pytest.toml leftover; HOLD not PASS |
| 2026-09-10 01:48:09 JST | clock-gate-0145 | completed | coordinator | operate/work; vacancy leftover now not wait 01:59 |
| 2026-09-10 01:48:09 JST | leftover-vacancy-0145a | completed | worker-1 | 14807 -c custom.ini displaces pyproject native on 9; HOLD no View |
| 2026-09-10 01:48:09 JST | leftover-vacancy-0145b | completed | worker-2 | 14807 -c custom.ini displaces pytest.toml/ini/setup.cfg; HOLD no View |
| 2026-09-10 01:48:09 JST | leftover-vacancy-0145c | completed | worker-3 | 14807 -c toml native displaces named pytest.toml on 9; HOLD no View |
| 2026-09-10 01:48:09 JST | contamination-0145 | completed | worker-1 | contamination clean |
| 2026-09-10 01:48:09 JST | no-collect-0145 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 01:48:09 JST | no-dream-0145 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 01:49:07 JST | leftover-reconstitute-0140a | completed | worker-1 | 5203 --ff swaps miss onto TestA; --nf still TestB; --sw hides miss; --maxfail=1 miss visible; HOLD no View |
| 2026-09-10 01:49:07 JST | leftover-reconstitute-0140b | completed | worker-2 | 14095 same as 5203 (--ff swaps, --sw hides, --nf still original); 14011 --ff still 2 fail; 14691 --ff still sample missing; HOLD no View |
| 2026-09-10 01:49:07 JST | leftover-reconstitute-0140c | completed | worker-3 | 13246 --lf still shadow fail; 14104 --lf 6 pass no last-failed; HOLD no View |
| 2026-09-10 01:49:07 JST | leftover-reconstitute-0143a | started | worker-1 | 13246 --ff/--nf/--sw leftover; HOLD not PASS |
| 2026-09-10 01:49:07 JST | leftover-reconstitute-0143b | started | worker-2 | 14011/14691 --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 01:49:07 JST | leftover-reconstitute-0143c | started | worker-3 | 5203/14095/14011/13246 --tb=line leftover; HOLD not PASS |
| 2026-09-10 01:50:12 JST | leftover-reconstitute-0143a | completed | worker-1 | 13246 --ff/--nf still shadow; --sw stuck on first fail; HOLD no View |
| 2026-09-10 01:50:12 JST | leftover-reconstitute-0143b | completed | worker-2 | 14011 --nf still 2 fail; --sw hides Test2; 14691 --nf/--sw still sample missing; HOLD no View |
| 2026-09-10 01:50:12 JST | leftover-reconstitute-0143c | completed | worker-3 | 5203/14095/14011/13246 --tb=line still miss; HOLD no View |
| 2026-09-10 01:50:12 JST | leftover-reconstitute-0146a | started | worker-1 | 13479 --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 01:50:12 JST | leftover-reconstitute-0146b | started | worker-2 | 14811/14737 --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 01:50:12 JST | leftover-reconstitute-0146c | started | worker-3 | 14104 --ff; 14004 --lf; 13246/14011 --maxfail leftover; HOLD not PASS |
| 2026-09-10 01:51:54 JST | leftover-reconstitute-0146a | completed | worker-1 | 13479 --ff/--sw still ff missing; HOLD no View |
| 2026-09-10 01:51:54 JST | leftover-reconstitute-0146b | completed | worker-2 | 14811 --nf/--sw still getini fail; 14737 --nf still 1 fail; HOLD no View |
| 2026-09-10 01:51:54 JST | leftover-reconstitute-0146c | completed | worker-3 | 14104 --ff 6 pass; 14004 --lf 4 pass; 13246 --maxfail=1 1 fail; 14011 --maxfail=1 hides Test2; HOLD no View |
| 2026-09-10 01:51:54 JST | leftover-reconstitute-0149a | started | worker-1 | 14812/14973/14447 --lf leftover; HOLD not PASS |
| 2026-09-10 01:51:54 JST | leftover-reconstitute-0149b | started | worker-2 | 14148/13699 --lf leftover; HOLD not PASS |
| 2026-09-10 01:51:54 JST | leftover-reconstitute-0149c | started | worker-3 | 14841/14488/14560 --lf leftover; HOLD not PASS |
| 2026-09-10 01:53:07 JST | leftover-reconstitute-0149a | completed | worker-1 | 14812 --lf still INTERNALERROR (test passed); 14447 --lf still 3 fail; 14973 --lf 2 pass; HOLD no View |
| 2026-09-10 01:53:07 JST | leftover-reconstitute-0149b | completed | worker-2 | 14148 --lf 1 pass; 13699 --lf still AttributeError; HOLD no View |
| 2026-09-10 01:53:07 JST | leftover-reconstitute-0149c | completed | worker-3 | 14841 --lf reruns resource_tracker fail; 14488 --lf reruns StashKey; 14560 --lf collect-error not last-failed; HOLD no View |
| 2026-09-10 01:53:07 JST | leftover-reconstitute-0152a | started | worker-1 | 14447/14841 --ff leftover; HOLD not PASS |
| 2026-09-10 01:53:07 JST | leftover-reconstitute-0152b | started | worker-2 | 14488/14560 --ff leftover; HOLD not PASS |
| 2026-09-10 01:53:07 JST | leftover-reconstitute-0152c | started | worker-3 | 14812/13699 --ff leftover; HOLD not PASS |
| 2026-09-10 01:54:15 JST | leftover-reconstitute-0152a | completed | worker-1 | 14447 --ff still 3 fail; 14841 --ff still resource_tracker first; HOLD no View |
| 2026-09-10 01:54:15 JST | leftover-reconstitute-0152b | completed | worker-2 | 14488 --ff still StashKey; 14560 --ff collect-error not last-failed; HOLD no View |
| 2026-09-10 01:54:15 JST | leftover-reconstitute-0152c | completed | worker-3 | 14812 --ff still INTERNALERROR after pass; 13699 --ff still AttributeError; HOLD no View |
| 2026-09-10 01:54:15 JST | leftover-reconstitute-0155a | started | worker-1 | 14447/14841 --sw leftover; HOLD not PASS |
| 2026-09-10 01:54:15 JST | leftover-reconstitute-0155b | started | worker-2 | 14488/14812 --sw leftover; HOLD not PASS |
| 2026-09-10 01:54:15 JST | leftover-reconstitute-0155c | started | worker-3 | 13699 --sw leftover; HOLD not PASS |
| 2026-09-10 01:55:28 JST | leftover-reconstitute-0155a | completed | worker-1 | 14447 --sw hides later walrus fails; 14841 --sw still resource_tracker; HOLD no View |
| 2026-09-10 01:55:28 JST | leftover-reconstitute-0155b | completed | worker-2 | 14488 --sw still StashKey; 14812 --sw still INTERNALERROR after pass; HOLD no View |
| 2026-09-10 01:55:28 JST | leftover-reconstitute-0155c | completed | worker-3 | 13699 --sw still AttributeError; HOLD no View |
| 2026-09-10 01:55:28 JST | leftover-reconstitute-0158a | started | worker-1 | 14447/14841 --nf leftover; HOLD not PASS |
| 2026-09-10 01:55:28 JST | leftover-reconstitute-0158b | started | worker-2 | 14488/14812 --nf leftover; HOLD not PASS |
| 2026-09-10 01:55:28 JST | leftover-reconstitute-0158c | started | worker-3 | 13699 --nf leftover; HOLD not PASS |
| 2026-09-10 01:56:39 JST | leftover-reconstitute-0158a | completed | worker-1 | 14447 --nf still 3 fail; 14841 --nf still 1 fail 3 pass; HOLD no View |
| 2026-09-10 01:56:39 JST | leftover-reconstitute-0158b | completed | worker-2 | 14488 --nf still StashKey; 14812 --nf still INTERNALERROR after pass; HOLD no View |
| 2026-09-10 01:56:39 JST | leftover-reconstitute-0158c | completed | worker-3 | 13699 --nf still AttributeError; HOLD no View |
| 2026-09-10 01:56:39 JST | leftover-reconstitute-0161a | started | worker-1 | 14973/14148 --ff leftover; HOLD not PASS |
| 2026-09-10 01:56:39 JST | leftover-reconstitute-0161b | started | worker-2 | 14762/14323 --lf leftover; HOLD not PASS |
| 2026-09-10 01:56:39 JST | leftover-reconstitute-0161c | started | worker-3 | 14560 --sw; 9298 --lf leftover; HOLD not PASS |
| 2026-09-10 01:57:21 JST | leftover-reconstitute-0161a | completed | worker-1 | 14973 --ff 2 pass; 14148 --ff 1 pass; HOLD no View |
| 2026-09-10 01:57:21 JST | leftover-reconstitute-0161b | completed | worker-2 | 14762/14323 --lf 1 pass; HOLD no View |
| 2026-09-10 01:57:21 JST | leftover-reconstitute-0161c | completed | worker-3 | 14560 --sw still collect-error; 9298 --lf 1 pass; HOLD no View |
| 2026-09-10 01:57:22 JST | leftover-reconstitute-0164a | started | worker-1 | next leftover extras after leftover-0161; HOLD not PASS |
| 2026-09-10 01:58:06 JST | leftover-reconstitute-0164a | completed | worker-1 | 14051 --lf 1; 14323/14762/9298 --ff pass; 14973/14148 --sw pass; HOLD no View |
| 2026-09-10 01:58:06 JST | leftover-reconstitute-0167a | started | worker-1 | next leftover extras after leftover-0164; HOLD not PASS |
| 2026-09-10 01:58:41 JST | leftover-reconstitute-0167a | completed | worker-1 | 14051 --ff/--nf/--sw pass; 14323/14762/9298 --sw 1 pass; HOLD no View |
| 2026-09-10 01:59:04 JST | leftover-reconstitute-0170a | started | worker-1 | 14819/14820/14445/14817/14448/13784 --lf leftover; HOLD not PASS |
| 2026-09-10 01:59:22 JST | leftover-reconstitute-0170a | completed | worker-1 | 14819/14820/14445/14817/14448 --lf still rewrite miss; 13784 --lf 1 pass (doubling is stdout); HOLD no View |
| 2026-09-10 01:59:53 JST | leftover-reconstitute-0173a | started | worker-1 | 14819/14820/14445/14817/14448 --ff leftover; HOLD not PASS |
| 2026-09-10 02:00:07 JST | leftover-reconstitute-0173a | completed | worker-1 | 14819/14820/14445/14817/14448 --ff still rewrite miss; HOLD no View |
| 2026-09-10 02:00:27 JST | leftover-reconstitute-0176a | started | worker-1 | 14819/14820/14445/14817/14448 --sw leftover; HOLD not PASS |
| 2026-09-10 02:00:46 JST | leftover-reconstitute-0176a | completed | worker-1 | 14819/14445 --sw hides later rewrite fails; 14820/14817/14448 --sw still miss; HOLD no View |
| 2026-09-10 02:01:36 JST | clock-gate-0201 | started | coordinator | operate/work; vacancy leftover now not wait 02:14 |
| 2026-09-10 02:01:36 JST | leftover-vacancy-0201a | started | worker-1 | 14807 -c toml [pytest] vs pyproject leftover; HOLD not PASS |
| 2026-09-10 02:01:36 JST | leftover-vacancy-0201b | started | worker-2 | 14807 -c toml native vs setup.cfg leftover; HOLD not PASS |
| 2026-09-10 02:01:36 JST | leftover-vacancy-0201c | started | worker-3 | 14807 -c ini vs tox/ini_options leftover; HOLD not PASS |
| 2026-09-10 02:02:39 JST | leftover-reconstitute-0179a | started | worker-1 | 14819/14445/14820 --nf leftover; HOLD not PASS |
| 2026-09-10 02:02:39 JST | leftover-reconstitute-0179b | started | worker-2 | 14817/14448 --nf; 13784 --ff/--sw/--nf leftover; HOLD not PASS |
| 2026-09-10 02:02:39 JST | leftover-reconstitute-0179c | started | worker-3 | 14815/14816/14389/14814 --lf leftover; HOLD not PASS |
| 2026-09-10 02:03:10 JST | clock-gate-0201 | completed | coordinator | operate/work; vacancy leftover now not wait 02:14 |
| 2026-09-10 02:03:10 JST | leftover-vacancy-0201a | completed | worker-1 | 14807 -c toml unread [pytest] displaces pyproject native on 9 (defaults); HOLD no View |
| 2026-09-10 02:03:10 JST | leftover-vacancy-0201b | completed | worker-2 | 14807 -c toml native vs setup.cfg 8.4.1 default / 9 native; HOLD no View |
| 2026-09-10 02:03:10 JST | leftover-vacancy-0201c | completed | worker-3 | 14807 -c ini displaces tox.ini and ini_options; HOLD no View |
| 2026-09-10 02:03:10 JST | contamination-0201 | completed | worker-1 | contamination clean |
| 2026-09-10 02:03:10 JST | no-collect-0201 | completed | worker-2 | NO_RUNNABLE_JOB; no resume |
| 2026-09-10 02:03:10 JST | no-dream-0201 | completed | worker-3 | THIN_WRAPPER; KEEP 0; no 保全 |
| 2026-09-10 02:03:55 JST | leftover-reconstitute-0179a | completed | worker-1 | 14819/14445/14820 --nf still rewrite miss; HOLD no View |
| 2026-09-10 02:03:55 JST | leftover-reconstitute-0179b | completed | worker-2 | 14817/14448 --nf still rewrite miss; 13784 --ff/--sw/--nf 1 pass (doubling is stdout); HOLD no View |
| 2026-09-10 02:03:55 JST | leftover-reconstitute-0179c | completed | worker-3 | 14815/14816/14389 --lf still fail; 14814 --lf reruns starred fail; HOLD no View |
| 2026-09-10 02:03:56 JST | leftover-reconstitute-0182a | started | worker-1 | 14815 --ff/--sw/--nf leftover; HOLD not PASS |
| 2026-09-10 02:03:56 JST | leftover-reconstitute-0182b | started | worker-2 | 14816/14389 --ff/--sw/--nf leftover; HOLD not PASS |
| 2026-09-10 02:03:56 JST | leftover-reconstitute-0182c | started | worker-3 | 14814 --ff/--sw/--nf; 14817/14448 --lf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:05:26 JST | leftover-reconstitute-0182a | completed | worker-1 | 14815 --ff/--nf still 1 fail; --sw stuck on first; HOLD no View |
| 2026-09-10 02:05:26 JST | leftover-reconstitute-0182b | completed | worker-2 | 14816/14389 --ff/--nf still 1 fail; --sw stuck on first; HOLD no View |
| 2026-09-10 02:05:26 JST | leftover-reconstitute-0182c | completed | worker-3 | 14814 --ff/--nf still starred; --sw 1 fail 2 deselected; 14817/14448 --sw hides later rewrite fail; HOLD no View |
| 2026-09-10 02:05:26 JST | leftover-reconstitute-0185a | started | worker-1 | 14819/14445/14447/14814/14448/14817 --maxfail=1 leftover; HOLD not PASS |
| 2026-09-10 02:05:26 JST | leftover-reconstitute-0185b | started | worker-2 | 14817/14448 --ff leftover; HOLD not PASS |
| 2026-09-10 02:05:26 JST | leftover-reconstitute-0185c | started | worker-3 | 14444/14271/14476 --lf leftover; HOLD not PASS |
| 2026-09-10 02:06:27 JST | leftover-reconstitute-0185a | completed | worker-1 | 14819/14445/14447/14448/14817 --maxfail=1 hides later rewrite fail; 14814 --maxfail=1 still starred after 2 pass; HOLD no View |
| 2026-09-10 02:06:27 JST | leftover-reconstitute-0185b | completed | worker-2 | 14817/14448 --ff still rewrite miss; 14820 --maxfail=1 1 fail; HOLD no View |
| 2026-09-10 02:06:27 JST | leftover-reconstitute-0185c | completed | worker-3 | 14444 parent --lf collect-error 4; 14271 --lf 2 pass; 14476 --lf -k foo 2 pass; HOLD no View |
| 2026-09-10 02:06:27 JST | leftover-reconstitute-0188a | started | worker-1 | 14444 isolated --lf leftover; HOLD not PASS |
| 2026-09-10 02:06:27 JST | leftover-reconstitute-0188b | started | worker-2 | 14815/14816/14448/14814/14817/14819 --assert=plain --lf leftover; HOLD not PASS |
| 2026-09-10 02:06:27 JST | leftover-reconstitute-0188c | started | worker-3 | 14445/14820/14389 --assert=plain --lf leftover; HOLD not PASS |
| 2026-09-10 02:07:59 JST | leftover-reconstitute-0188a | completed | worker-1 | 14444 isolated --lf 2 pass no last-failed; HOLD no View |
| 2026-09-10 02:07:59 JST | leftover-reconstitute-0188b | completed | worker-2 | 14815/14816/14448/14817 --assert=plain --lf still fail; 14814 plain --lf 3 pass; HOLD no View |
| 2026-09-10 02:07:59 JST | leftover-reconstitute-0188c | completed | worker-3 | 14819 --assert=plain 1 fail 1 pass (hides boom); 14445/14820 plain 2 pass; 14389 plain --lf still fail; HOLD no View |
| 2026-09-10 02:07:59 JST | leftover-reconstitute-0191a | started | worker-1 | 14819 --assert=plain --ff/--sw/--nf leftover; HOLD not PASS |
| 2026-09-10 02:07:59 JST | leftover-reconstitute-0191b | started | worker-2 | 14445/14820 --assert=plain --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:07:59 JST | leftover-reconstitute-0191c | started | worker-3 | 14815/14816/14817 --assert=plain --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:09:11 JST | leftover-reconstitute-0191a | completed | worker-1 | 14819 --assert=plain --ff/--nf 1 fail 1 pass; --sw stuck on first fail; HOLD no View |
| 2026-09-10 02:09:12 JST | leftover-reconstitute-0191b | completed | worker-2 | 14445/14820 --assert=plain --ff/--sw 2 pass no last-failed; HOLD no View |
| 2026-09-10 02:09:12 JST | leftover-reconstitute-0191c | completed | worker-3 | 14815/14816/14817 --assert=plain --ff still fail; --sw hides later 14817; HOLD no View |
| 2026-09-10 02:09:12 JST | leftover-reconstitute-0194a | started | worker-1 | 14447 --assert=plain --lf/--ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:09:12 JST | leftover-reconstitute-0194b | started | worker-2 | 14448/14814 --assert=plain --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:09:12 JST | leftover-reconstitute-0194c | started | worker-3 | 14389/13784 --assert=plain leftover; HOLD not PASS |
| 2026-09-10 02:10:25 JST | leftover-reconstitute-0194a | completed | worker-1 | 14447 --assert=plain 3 pass no last-failed; HOLD no View |
| 2026-09-10 02:10:25 JST | leftover-reconstitute-0194b | completed | worker-2 | 14448 plain --ff still 2 fail; 14814 plain --ff 3 pass; HOLD no View |
| 2026-09-10 02:10:25 JST | leftover-reconstitute-0194c | completed | worker-3 | 14389 plain --ff still fail; 13784 plain --lf 1 pass; HOLD no View |
| 2026-09-10 02:10:25 JST | leftover-reconstitute-0197a | started | worker-1 | 14800 --assert=plain --lf/--ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:10:25 JST | leftover-reconstitute-0197b | started | worker-2 | 14775 -Werror --assert=plain leftover; HOLD not PASS |
| 2026-09-10 02:10:25 JST | leftover-reconstitute-0197c | started | worker-3 | 13755b/13885 --assert=plain --lf; 14635/13882 --lf leftover; HOLD not PASS |
| 2026-09-10 02:11:41 JST | leftover-reconstitute-0197a | completed | worker-1 | 14800 --assert=plain still _finalizers from 9.1.0; --lf/--ff/--sw hide it; HOLD no View |
| 2026-09-10 02:11:41 JST | leftover-reconstitute-0197b | completed | worker-2 | 14775 -Werror --assert=plain still 2 errors on 9.1.0; --sw hides second; HOLD no View |
| 2026-09-10 02:11:41 JST | leftover-reconstitute-0197c | completed | worker-3 | 13755b plain --lf hides session miss; 13885 plain --lf still 8/9; 14635/13882 --lf 4/2 pass; HOLD no View |
| 2026-09-10 02:11:41 JST | leftover-reconstitute-0203a | started | worker-1 | 14800/14775 --assert=plain --nf leftover; HOLD not PASS |
| 2026-09-10 02:11:41 JST | leftover-reconstitute-0203b | started | worker-2 | 13755b --assert=plain --ff/--sw/--nf leftover; HOLD not PASS |
| 2026-09-10 02:11:41 JST | leftover-reconstitute-0203c | started | worker-3 | 14640/14971/14964d --assert=plain --lf leftover; HOLD not PASS |
| 2026-09-10 02:12:56 JST | leftover-reconstitute-0203a | completed | worker-1 | 14800/14775 --assert=plain --nf still 9.1.0 errors; HOLD no View |
| 2026-09-10 02:12:56 JST | leftover-reconstitute-0203b | completed | worker-2 | 13755b plain --ff swaps miss; --sw hides; --nf still 2 errors; HOLD no View |
| 2026-09-10 02:12:56 JST | leftover-reconstitute-0203c | completed | worker-3 | 14640/14971 plain --lf 9.1.0 later error; 14964d plain --lf later miss not last-failed; HOLD no View |
| 2026-09-10 02:12:56 JST | leftover-reconstitute-0206a | started | worker-1 | 5203 --assert=plain --lf/--ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:12:56 JST | leftover-reconstitute-0206b | started | worker-2 | 14095 --assert=plain --lf/--ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:12:56 JST | leftover-reconstitute-0206c | started | worker-3 | 13246/14011 --assert=plain --lf; 14800 --maxfail=1 --assert=plain leftover; HOLD not PASS |
| 2026-09-10 02:14:00 JST | leftover-reconstitute-0206a | completed | worker-1 | 5203 --assert=plain --lf/--sw hide rebuild miss; --ff swaps; HOLD no View |
| 2026-09-10 02:14:00 JST | leftover-reconstitute-0206b | completed | worker-2 | 14095 --assert=plain --lf/--sw hide rebuild miss; --ff swaps; HOLD no View |
| 2026-09-10 02:14:00 JST | leftover-reconstitute-0206c | completed | worker-3 | 13246/14011 plain --lf still fail; 14800 --maxfail=1 plain hides second _finalizers; HOLD no View |
| 2026-09-10 02:14:00 JST | leftover-reconstitute-0209a | started | worker-1 | 14640/14971 --assert=plain --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:14:00 JST | leftover-reconstitute-0209b | started | worker-2 | 14964d --assert=plain --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:14:00 JST | leftover-reconstitute-0209c | started | worker-3 | 14101/14011 --assert=plain leftover; HOLD not PASS |
| 2026-09-10 02:15:07 JST | leftover-reconstitute-0209a | completed | worker-1 | 14640/14971 plain --ff later miss visible; --sw stuck on later ERROR; HOLD no View |
| 2026-09-10 02:15:07 JST | leftover-reconstitute-0209b | completed | worker-2 | 14964d plain --ff later also ERROR; --sw hides later miss; HOLD no View |
| 2026-09-10 02:15:07 JST | leftover-reconstitute-0209c | completed | worker-3 | 14101 plain --lf XPASS not last-failed; 14011 plain --ff still 2 fail; --sw hides Test2; HOLD no View |
| 2026-09-10 02:15:07 JST | leftover-reconstitute-0212a | started | worker-1 | 14640/14971/14964d --assert=plain --nf leftover; HOLD not PASS |
| 2026-09-10 02:15:07 JST | leftover-reconstitute-0212b | started | worker-2 | 14101 --assert=plain --ff/--sw/--nf leftover; HOLD not PASS |
| 2026-09-10 02:15:07 JST | leftover-reconstitute-0212c | started | worker-3 | 13885 --assert=plain --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:16:06 JST | leftover-reconstitute-0212a | completed | worker-1 | 14640/14971 plain --nf later miss visible; 14964d plain --nf later also ERROR; HOLD no View |
| 2026-09-10 02:16:06 JST | leftover-reconstitute-0212b | completed | worker-2 | 14101 plain --ff/--nf still XPASS; --sw hides xpass; HOLD no View |
| 2026-09-10 02:16:06 JST | leftover-reconstitute-0212c | completed | worker-3 | 13885 plain --ff/--sw still 8/9 skip-vs-fire; HOLD no View |
| 2026-09-10 02:16:06 JST | leftover-reconstitute-0215a | started | worker-1 | 14700/14683/14702 --lf leftover; HOLD not PASS |
| 2026-09-10 02:16:06 JST | leftover-reconstitute-0215b | started | worker-2 | 14004 --ff; 13965/13754 --lf leftover; HOLD not PASS |
| 2026-09-10 02:16:06 JST | leftover-reconstitute-0215c | started | worker-3 | 14104/9298 --nf leftover; HOLD not PASS |
| 2026-09-10 02:16:28 JST | leftover-reconstitute-0215a | completed | worker-1 | 14700/14683/14702 --lf pass (miss not last-failed); HOLD no View |
| 2026-09-10 02:16:28 JST | leftover-reconstitute-0215b | completed | worker-2 | 14004 --ff 4 pass; 13965/13754 --lf pass; HOLD no View |
| 2026-09-10 02:16:28 JST | leftover-reconstitute-0215c | completed | worker-3 | 14104/9298 --nf pass; HOLD no View |
| 2026-09-10 02:16:54 JST | leftover-reconstitute-0218a | started | worker-1 | 14700/14683/14702 --ff leftover; HOLD not PASS |
| 2026-09-10 02:16:54 JST | leftover-reconstitute-0218b | started | worker-2 | 14004 --nf; 13965/13754 --ff leftover; HOLD not PASS |
| 2026-09-10 02:16:54 JST | leftover-reconstitute-0218c | started | worker-3 | 11502/14431 --lf leftover; HOLD not PASS |
| 2026-09-10 02:17:16 JST | leftover-reconstitute-0218a | completed | worker-1 | 14700/14683/14702 --ff pass/skip; HOLD no View |
| 2026-09-10 02:17:16 JST | leftover-reconstitute-0218b | completed | worker-2 | 14004 --nf 4 pass; 13965/13754 --ff pass; HOLD no View |
| 2026-09-10 02:17:16 JST | leftover-reconstitute-0218c | completed | worker-3 | 11502/14431 --lf 1 pass; HOLD no View |
| 2026-09-10 02:18:50 JST | leftover-reconstitute-0221a | started | worker-1 | 14412/13957/14877 --lf leftover; HOLD not PASS |
| 2026-09-10 02:18:50 JST | leftover-reconstitute-0221b | started | worker-2 | 14323/14762/14051 --nf leftover; HOLD not PASS |
| 2026-09-10 02:18:50 JST | leftover-reconstitute-0221c | started | worker-3 | 14431/11502 --ff leftover; HOLD not PASS |
| 2026-09-10 02:19:20 JST | leftover-reconstitute-0221a | completed | worker-1 | 14412/13957/14877 --lf pass or plugin count; HOLD no View |
| 2026-09-10 02:19:20 JST | leftover-reconstitute-0221b | completed | worker-2 | 14323/14762/14051 --nf pass; HOLD no View |
| 2026-09-10 02:19:20 JST | leftover-reconstitute-0221c | completed | worker-3 | 14431/11502 --ff 1 pass; HOLD no View |
| 2026-09-10 02:20:03 JST | leftover-reconstitute-0224a | started | worker-1 | 14412/13957/14877 --ff leftover; HOLD not PASS |
| 2026-09-10 02:20:03 JST | leftover-reconstitute-0224b | started | worker-2 | 14323/14762/14051 --ff leftover; HOLD not PASS |
| 2026-09-10 02:20:03 JST | leftover-reconstitute-0224c | started | worker-3 | 13957b --lf; 9703b --nf leftover; HOLD not PASS |
| 2026-09-10 02:20:23 JST | leftover-reconstitute-0224a | completed | worker-1 | 14412/13957/14877 --ff pass; HOLD no View |
| 2026-09-10 02:20:23 JST | leftover-reconstitute-0224b | completed | worker-2 | 14323/14762/14051 --ff pass; HOLD no View |
| 2026-09-10 02:20:23 JST | leftover-reconstitute-0224c | completed | worker-3 | 13957b --lf 4 pass; 9703b --nf 2 pass; HOLD no View |
| 2026-09-10 02:20:47 JST | leftover-reconstitute-0227a | started | worker-1 | 13957b --ff; 9703b leftover; HOLD not PASS |
| 2026-09-10 02:20:47 JST | leftover-reconstitute-0227b | started | worker-2 | 14412/13957 --nf; 13755 --lf leftover; HOLD not PASS |
| 2026-09-10 02:20:47 JST | leftover-reconstitute-0227c | started | worker-3 | 14650b --ff/--nf leftover; HOLD not PASS |
| 2026-09-10 02:21:16 JST | leftover-reconstitute-0227a | completed | worker-1 | 13957b --ff 4 pass; 9703b leftover 2 pass; HOLD no View |
| 2026-09-10 02:21:16 JST | leftover-reconstitute-0227b | completed | worker-2 | 14412/13957 --nf pass; 13755 --lf pass; HOLD no View |
| 2026-09-10 02:21:16 JST | leftover-reconstitute-0227c | completed | worker-3 | 14650b --ff/--nf 2 pass no last-failed; HOLD no View |
| 2026-09-10 02:21:41 JST | leftover-reconstitute-0230a | started | worker-1 | 13755 --ff/--nf leftover; HOLD not PASS |
| 2026-09-10 02:21:41 JST | leftover-reconstitute-0230b | started | worker-2 | 14476/14271 --ff leftover; HOLD not PASS |
| 2026-09-10 02:21:41 JST | leftover-reconstitute-0230c | started | worker-3 | 14700/14683 --nf leftover; HOLD not PASS |
| 2026-09-10 02:22:05 JST | leftover-reconstitute-0230a | completed | worker-1 | 13755 --ff/--nf pass; HOLD no View |
| 2026-09-10 02:22:05 JST | leftover-reconstitute-0230b | completed | worker-2 | 14476/14271 --ff pass; HOLD no View |
| 2026-09-10 02:22:05 JST | leftover-reconstitute-0230c | completed | worker-3 | 14700/14683 --nf pass/skip; HOLD no View |
| 2026-09-10 02:26:17 JST | leftover-reconstitute-0233a | started | worker-1 | 13755/14476/14271 --sw leftover; HOLD not PASS |
| 2026-09-10 02:26:17 JST | leftover-reconstitute-0233b | started | worker-2 | 14700/14683/14702/14004 --sw leftover; HOLD not PASS |
| 2026-09-10 02:26:17 JST | leftover-reconstitute-0233c | started | worker-3 | 13957b/13965/13754/11502/14431/14877 --nf/--sw; 14716/3062/14808 --lf leftover; HOLD not PASS |
| 2026-09-10 02:28:11 JST | leftover-reconstitute-0233a | completed | worker-1 | 13755/14476/14271 --sw pass (no last-failed); HOLD no View |
| 2026-09-10 02:28:11 JST | leftover-reconstitute-0233b | completed | worker-2 | 14700 --sw 1 skip; 14683/14702/14004 --sw pass; HOLD no View |
| 2026-09-10 02:28:11 JST | leftover-reconstitute-0233c | completed | worker-3 | 11502 -p no:cacheprovider --nf/--sw unrecognized; 14412 parent --sw collect collision; 14877 no test_ files rc=5; 14716/3062/14808 --lf pass; HOLD no View |
| 2026-09-10 02:28:11 JST | leftover-reconstitute-0236a | started | worker-1 | 14412 isolated --nf/--sw; 11502 --nf/--sw keep cacheprovider; 14877 count.py leftover; HOLD not PASS |
| 2026-09-10 02:28:11 JST | leftover-reconstitute-0236b | started | worker-2 | 13957 --sw; 13882/14635 --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:28:11 JST | leftover-reconstitute-0236c | started | worker-3 | 14716/14808/3062 --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:30:05 JST | leftover-reconstitute-0236a | completed | worker-1 | 14412 isolated --nf/--sw 1 pass; 11502 --nf/--sw with cacheprovider 1 pass; 14877 count.py rc=5; HOLD no View |
| 2026-09-10 02:30:05 JST | leftover-reconstitute-0236b | completed | worker-2 | 13957 --sw 1 pass; 13882/14635 --nf/--sw pass; HOLD no View |
| 2026-09-10 02:30:05 JST | leftover-reconstitute-0236c | completed | worker-3 | 14716/14808/3062 --ff/--sw 1 pass; HOLD no View |
| 2026-09-10 02:30:05 JST | leftover-reconstitute-0239a | started | worker-1 | 14808 tool_pytest --lf/--ff/--sw; 13985 --lf leftover; HOLD not PASS |
| 2026-09-10 02:30:05 JST | leftover-reconstitute-0239b | started | worker-2 | 14255 int_native/quoted leftover; HOLD not PASS |
| 2026-09-10 02:30:05 JST | leftover-reconstitute-0239c | started | worker-3 | 14650c --nf/--sw; 14613 --lf/--ff; 14696 iso_miss --lf; 14048 --lf leftover; HOLD not PASS |
| 2026-09-10 02:31:23 JST | leftover-reconstitute-0239a | completed | worker-1 | 14808 tool_pytest --lf 8.4.1 pass / pytest9 TypeError still; 13985 string TypeError still / list pass; HOLD no View |
| 2026-09-10 02:31:23 JST | leftover-reconstitute-0239b | completed | worker-2 | 14255 int_native --lf TypeError on 9 not last-failed; quoted --lf 1 pass; HOLD no View |
| 2026-09-10 02:31:23 JST | leftover-reconstitute-0239c | completed | worker-3 | 14650c --nf/--sw collect-error not last-failed; 14613/14696/14048 --lf pass; HOLD no View |
| 2026-09-10 02:31:23 JST | leftover-reconstitute-0242a | started | worker-1 | 13985 --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:31:23 JST | leftover-reconstitute-0242b | started | worker-2 | 14255 int_native --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:31:23 JST | leftover-reconstitute-0242c | started | worker-3 | 14613/14696 --nf/--sw; 14048 --ff leftover; HOLD not PASS |
| 2026-09-10 02:32:48 JST | leftover-reconstitute-0242a | completed | worker-1 | 13985 string --ff/--sw still TypeError on 9; ini_options --lf 1 pass; HOLD no View |
| 2026-09-10 02:32:48 JST | leftover-reconstitute-0242b | completed | worker-2 | 14255 int_native --nf/--sw still TypeError on 9 not last-failed; HOLD no View |
| 2026-09-10 02:32:48 JST | leftover-reconstitute-0242c | completed | worker-3 | 14613/14696 --nf/--sw pass; 14048 --ff 1 pass; HOLD no View |
| 2026-09-10 02:32:48 JST | leftover-reconstitute-0245a | started | worker-1 | 14253/14092 --lf leftover; HOLD not PASS |
| 2026-09-10 02:32:48 JST | leftover-reconstitute-0245b | started | worker-2 | 14808 ini_options --lf; 14560/14148 --nf leftover; HOLD not PASS |
| 2026-09-10 02:32:48 JST | leftover-reconstitute-0245c | started | worker-3 | 13985 list --ff/--sw; 14705 --lf leftover; HOLD not PASS |
| 2026-09-10 02:41:06 JST | leftover-reconstitute-0245a | completed | worker-1 | 14253/14092 parent --lf leftover dummy collisions on 8.4.1 / TypeError on pytest 9; isolated ini_options --lf 1 pass; HOLD no View |
| 2026-09-10 02:41:06 JST | leftover-reconstitute-0245b | completed | worker-2 | 14808 ini_options --lf still list AssertionError; 14560 --nf collect-error KeyError; 14148 --nf 1 pass; HOLD no View |
| 2026-09-10 02:41:06 JST | leftover-reconstitute-0245c | completed | worker-3 | 13985 list --ff/--sw 1 pass; 14705 --lf 1 pass; HOLD no View |
| 2026-09-10 02:41:06 JST | leftover-reconstitute-0248a | started | worker-1 | 14253/14092 isolated --ff/--nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:41:06 JST | leftover-reconstitute-0248b | started | worker-2 | 14808 ini_options --ff/--nf/--sw; tool_pytest --nf; 14705 --ff/--nf/--sw; 14560 --maxfail=1 leftover; HOLD not PASS |
| 2026-09-10 02:41:06 JST | leftover-reconstitute-0248c | started | worker-3 | 13985 list --nf / ini_options --ff/--nf/--sw / string --nf; 14255 quoted --ff/--nf; 14048 --sw/--nf leftover; HOLD not PASS |
| 2026-09-10 02:43:28 JST | leftover-reconstitute-0248a | completed | worker-1 | 14253/14092 isolated --ff/--nf/--sw 1 pass; HOLD no View |
| 2026-09-10 02:43:28 JST | leftover-reconstitute-0248b | completed | worker-2 | 14808 ini_options --ff/--nf/--sw still list AssertionError; tool_pytest --nf 8.4.1 pass / pytest9 TypeError still; 14705 --ff/--nf/--sw 1 pass; 14560 --maxfail=1 still collect-error; HOLD no View |
| 2026-09-10 02:43:28 JST | leftover-reconstitute-0248c | completed | worker-3 | 13985 list/ini_options --nf/--ff/--sw 1 pass; string --nf TypeError on 9 not last-failed; 14255 quoted --ff/--nf 1 pass; 14048 --sw/--nf 1 pass; HOLD no View |
| 2026-09-10 02:43:28 JST | leftover-reconstitute-0251a | started | worker-1 | 14412 isolated --lf/--ff leftover; HOLD not PASS |
| 2026-09-10 02:43:28 JST | leftover-reconstitute-0251b | started | worker-2 | 14004b --ff/--nf/--sw; 14808 pytest_ini --nf; 14650c/13985/14255/14808 --maxfail=1 leftover; HOLD not PASS |
| 2026-09-10 02:43:28 JST | leftover-reconstitute-0251c | started | worker-3 | 11502 --cache-show; 14608c alt_inside --lf/--ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:47:38 JST | leftover-reconstitute-0251a | completed | worker-1 | 14412 isolated --lf/--ff 1 pass; HOLD no View |
| 2026-09-10 02:47:38 JST | leftover-reconstitute-0251b | completed | worker-2 | 14004b --ff/--nf/--sw 3 pass; 14808 pytest_ini --nf 1 pass; 14650c --maxfail=1 collect-error on 9; 13985/14255 --maxfail=1 TypeError on 9 not last-failed; 14808 tool --maxfail=1 TypeError still; HOLD no View |
| 2026-09-10 02:47:38 JST | leftover-reconstitute-0251c | completed | worker-3 | 11502 --cache-show after run lists ::test_a; 14608c alt_inside --lf/--ff/--sw 1 pass including 9.1.0; HOLD no View |
| 2026-09-10 02:47:38 JST | leftover-reconstitute-0254a | started | worker-1 | 14650c ini_options --lf/--ff/--nf/--sw; 14608c --nf; 13913 no-path --ff/--sw leftover; HOLD not PASS |
| 2026-09-10 02:47:38 JST | leftover-reconstitute-0254b | started | worker-2 | --maxfail leftovers 14412/14004b/14808/13985/14255/14696; HOLD not PASS |
| 2026-09-10 02:47:38 JST | leftover-reconstitute-0254c | started | worker-3 | 11502 --cache-clear; 14048 --maxfail leftover; HOLD not PASS |
| 2026-09-10 02:50:14 JST | leftover-reconstitute-0254a | completed | worker-1 | 14650c ini_options --lf/--ff/--nf/--sw collect-error on 9; 14608c --nf 1 pass; 13913 no-path --ff/--sw 8.4.1 pass / pytest9 unrecognized; HOLD no View |
| 2026-09-10 02:50:14 JST | leftover-reconstitute-0254b | completed | worker-2 | --maxfail=1 pass minis 1/3 pass; HOLD no View |
| 2026-09-10 02:50:14 JST | leftover-reconstitute-0254c | completed | worker-3 | 11502 --cache-clear 1 pass; 14048 --maxfail=1 1 pass; HOLD no View |
| 2026-09-10 02:50:14 JST | leftover-reconstitute-0257a | started | worker-1 | 14608c alt_lo_base --lf/--ff/--nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:50:14 JST | leftover-reconstitute-0257b | started | worker-2 | 13913 tests/ --ff/--sw; 14514c importlib --lf/--ff/--sw; 13922 leftover; HOLD not PASS |
| 2026-09-10 02:50:14 JST | leftover-reconstitute-0257c | started | worker-3 | 14431 alt_pyfiles; 14084 --pyargs --lf/--ff leftover; HOLD not PASS |
| 2026-09-10 02:52:22 JST | leftover-reconstitute-0257a | completed | worker-1 | 14608c alt_lo_base --lf/--ff/--nf/--sw 9.1.0 unrecognized not last-failed; HOLD no View |
| 2026-09-10 02:52:22 JST | leftover-reconstitute-0257b | completed | worker-2 | 13913 tests/ --ff/--sw 1 pass; 14514c importlib --lf/--ff/--sw 1 pass; 13922 --lf/--ff/--sw 1 pass; HOLD no View |
| 2026-09-10 02:52:22 JST | leftover-reconstitute-0257c | completed | worker-3 | 14431 alt_pyfiles --lf/--ff/--sw 1 pass; 14084 PYTHONPATH --lf/--ff 1 pass; HOLD no View |
| 2026-09-10 02:52:22 JST | leftover-reconstitute-0260a | started | worker-1 | 14514c default --lf/--ff/--sw; 14608c alt_lo_base --maxfail leftover; HOLD not PASS |
| 2026-09-10 02:52:22 JST | leftover-reconstitute-0260b | started | worker-2 | 13913 tests/ --lf/--nf; 13922 -- extra; 14084 --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:52:22 JST | leftover-reconstitute-0260c | started | worker-3 | 14431 alt_pyfiles --nf; 14514c importlib --nf; 13922 --nf leftover; HOLD not PASS |
| 2026-09-10 02:54:35 JST | leftover-reconstitute-0260a | completed | worker-1 | 14514c default --lf/--ff/--sw collect ImportError not last-failed; 14608c alt_lo_base --maxfail=1 9.1.0 unrecognized; HOLD no View |
| 2026-09-10 02:54:36 JST | leftover-reconstitute-0260b | completed | worker-2 | 13913 tests/ --lf/--nf 1 pass; 13922 -- extra rc=4 not last-failed; 14084 --nf/--sw 1 pass; HOLD no View |
| 2026-09-10 02:54:36 JST | leftover-reconstitute-0260c | completed | worker-3 | 14431 alt_pyfiles --nf 1 pass; 14514c importlib --nf 1 pass; 13922 --nf 1 pass; HOLD no View |
| 2026-09-10 02:54:36 JST | leftover-reconstitute-0263a | started | worker-1 | 14094 --lf/--ff/--nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:54:36 JST | leftover-reconstitute-0263b | started | worker-2 | 14916 --lf/--ff/--nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:54:36 JST | leftover-reconstitute-0263c | started | worker-3 | 14094b --lf/--ff/--sw; 14811 --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:55:15 JST | leftover-reconstitute-0260a | completed | worker-1 | 14514c default --lf/--ff/--sw collect ImportError all; 14608c alt_lo_base --maxfail=1 9.1.0 unrecognized not last-failed; HOLD no View |
| 2026-09-10 02:55:15 JST | leftover-reconstitute-0260b | completed | worker-2 | 13913 tests/ --lf/--nf 1 pass; 13922 extra two-phase rc=4 file-not-found; 14084 --nf/--sw 1 pass; HOLD no View |
| 2026-09-10 02:55:15 JST | leftover-reconstitute-0260c | completed | worker-3 | 14431 alt_pyfiles --nf 1 pass; 14514c importlib --nf 1 pass; 13922 --nf 1 pass; HOLD no View |
| 2026-09-10 02:55:15 JST | leftover-reconstitute-0263a | started | worker-1 | 14807 pytest.cfg vs native/ini/tox leftover; HOLD not PASS |
| 2026-09-10 02:55:15 JST | leftover-reconstitute-0263b | started | worker-2 | 14807 pytest.cfg vs setup.cfg/toml/ini_options leftover; HOLD not PASS |
| 2026-09-10 02:55:15 JST | leftover-reconstitute-0263c | started | worker-3 | 14807 -c vs pytest.cfg; tox.ini vs setup.cfg leftover; HOLD not PASS |
| 2026-09-10 02:56:20 JST | leftover-reconstitute-0263a | completed | worker-1 | 14094 --lf/--ff/--nf still 2 fail; --sw hides later; HOLD no View |
| 2026-09-10 02:56:20 JST | leftover-reconstitute-0263b | completed | worker-2 | 14916 --lf/--ff/--nf still 2 fail; --sw hides later; HOLD no View |
| 2026-09-10 02:56:20 JST | leftover-reconstitute-0263c | completed | worker-3 | 14094b --lf reruns 2 fail; --sw hides later; 14811 parent --nf/--sw 1 pass; HOLD no View |
| 2026-09-10 02:56:20 JST | leftover-reconstitute-0266a | started | worker-1 | 14436 caplog leftover rerun flags; HOLD not PASS |
| 2026-09-10 02:56:20 JST | leftover-reconstitute-0266b | started | worker-2 | 14094/14916 --maxfail; 14094b --nf leftover; HOLD not PASS |
| 2026-09-10 02:56:20 JST | leftover-reconstitute-0266c | started | worker-3 | 14811 implicit --ff; 14436 nolog leftover; HOLD not PASS |
| 2026-09-10 02:56:40 JST | leftover-reconstitute-0263a | completed | worker-1 | 14807 pytest.cfg vs native 8.4.1 default / pytest9 native; vs pytest.ini only_ini; vs tox.ini only_tox; HOLD no View |
| 2026-09-10 02:56:40 JST | leftover-reconstitute-0263b | completed | worker-2 | 14807 pytest.cfg vs setup.cfg only_cfg; vs toml 8.4.1 default / pytest9 toml; vs ini_options only_iniopt; HOLD no View |
| 2026-09-10 02:56:40 JST | leftover-reconstitute-0263c | completed | worker-3 | 14807 -c ini vs pytest.cfg only_cini; -c toml unread vs pytest.cfg default; tox.ini beats setup.cfg only_tox; HOLD no View |
| 2026-09-10 02:58:07 JST | leftover-reconstitute-0266a | completed | worker-1 | 14436 happy/nolog --lf/--ff/--sw 1 pass; session_fix --lf/--sw still ScopeMismatch; HOLD no View |
| 2026-09-10 02:58:07 JST | leftover-reconstitute-0266b | completed | worker-2 | 14094/14916 --maxfail=1 hides later fail; 14094b --nf still 2 fail 1 pass; HOLD no View |
| 2026-09-10 02:58:07 JST | leftover-reconstitute-0266c | completed | worker-3 | 14811 implicit --ff still 1 fail getini; HOLD no View |
| 2026-09-10 02:58:07 JST | leftover-reconstitute-0269a | started | worker-1 | 14436 session_fix --ff/--nf/--maxfail leftover; HOLD not PASS |
| 2026-09-10 02:58:07 JST | leftover-reconstitute-0269b | started | worker-2 | 14811 implicit --maxfail; 14488 --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 02:58:07 JST | leftover-reconstitute-0269c | started | worker-3 | 14841 --nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 02:59:50 JST | leftover-reconstitute-0269a | completed | worker-1 | 14436 session_fix --ff/--nf/--maxfail still ScopeMismatch; HOLD no View |
| 2026-09-10 02:59:50 JST | leftover-reconstitute-0269b | completed | worker-2 | 14811 implicit --maxfail still 1 fail; 14488 --nf still StashKey; --sw hides later pass; HOLD no View |
| 2026-09-10 02:59:50 JST | leftover-reconstitute-0269c | completed | worker-3 | 14841 --nf 8.4.1 1 fail 3 pass / pytest 9.1.0 4 pass flake; --sw hides later; HOLD no View |
| 2026-09-10 02:59:50 JST | leftover-reconstitute-0272a | started | worker-1 | 14812/14737 --maxfail leftover; HOLD not PASS |
| 2026-09-10 02:59:50 JST | leftover-reconstitute-0272b | started | worker-2 | 13699 --maxfail leftover; HOLD not PASS |
| 2026-09-10 02:59:50 JST | leftover-reconstitute-0272c | started | worker-3 | 14488/14841 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:01:26 JST | leftover-reconstitute-0272a | completed | worker-1 | 14812 --maxfail=1 still INTERNALERROR after pass rc=3; 14737 --maxfail=1 still 1 fail; HOLD no View |
| 2026-09-10 03:01:26 JST | leftover-reconstitute-0272b | completed | worker-2 | 13699 --maxfail=1 still AttributeError; HOLD no View |
| 2026-09-10 03:01:26 JST | leftover-reconstitute-0272c | completed | worker-3 | 14841 --maxfail=1 still 1 fail 3 pass; HOLD no View |
| 2026-09-10 03:01:26 JST | leftover-reconstitute-0275a | started | worker-1 | 14488 test_handler --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:01:26 JST | leftover-reconstitute-0275b | started | worker-2 | 14973 --nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 03:01:26 JST | leftover-reconstitute-0275c | started | worker-3 | 14702/9298 --nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 03:02:17 JST | leftover-reconstitute-0275a | completed | worker-1 | 14488 test_handler --maxfail=1 still 1 fail 1 pass StashKey; HOLD no View |
| 2026-09-10 03:02:17 JST | leftover-reconstitute-0275b | completed | worker-2 | 14973 --nf/--sw/--maxfail 2 pass (cleanup miss not last-failed); HOLD no View |
| 2026-09-10 03:02:17 JST | leftover-reconstitute-0275c | completed | worker-3 | 14702 --nf/--sw/--maxfail 2 pass 1 skip; 9298 --nf/--sw/--maxfail 1 pass; HOLD no View |
| 2026-09-10 03:02:17 JST | leftover-reconstitute-0278a | started | worker-1 | 14323 --nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 03:02:17 JST | leftover-reconstitute-0278b | started | worker-2 | 14762 --nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 03:02:17 JST | leftover-reconstitute-0278c | started | worker-3 | 14051 --lf/--nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 03:03:22 JST | leftover-reconstitute-0278a | completed | worker-1 | 14323 --nf/--sw/--maxfail 1 pass; HOLD no View |
| 2026-09-10 03:03:22 JST | leftover-reconstitute-0278b | completed | worker-2 | 14762 --nf/--sw/--maxfail 1 pass; HOLD no View |
| 2026-09-10 03:03:22 JST | leftover-reconstitute-0278c | completed | worker-3 | 14051 --lf/--nf/--sw/--maxfail 1 pass; HOLD no View |
| 2026-09-10 03:03:22 JST | leftover-reconstitute-0281a | started | worker-1 | 14683 --nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 03:03:22 JST | leftover-reconstitute-0281b | started | worker-2 | 14700 --maxfail; 13882 leftover; HOLD not PASS |
| 2026-09-10 03:03:22 JST | leftover-reconstitute-0281c | started | worker-3 | 14635 --nf/--sw/--maxfail leftover; HOLD not PASS |
| 2026-09-10 03:04:00 JST | leftover-reconstitute-0284a | started | worker-1 | 14807 setup.cfg [pytest] vs tox/ini/native leftover; HOLD not PASS |
| 2026-09-10 03:04:00 JST | leftover-reconstitute-0284b | started | worker-2 | 14807 pytest.ini [tool:pytest] vs pytest.cfg/tox leftover; HOLD not PASS |
| 2026-09-10 03:04:00 JST | leftover-reconstitute-0284c | started | worker-3 | 14807 -c toml native / -c ini [tool:pytest] vs pytest.cfg leftover; HOLD not PASS |
| 2026-09-10 03:04:05 JST | leftover-reconstitute-0281a | completed | worker-1 | 14683 leftover --nf/--sw/--maxfail on disk; HOLD no View |
| 2026-09-10 03:04:05 JST | leftover-reconstitute-0281b | completed | worker-2 | 14700/13882 leftover on disk; HOLD no View |
| 2026-09-10 03:04:05 JST | leftover-reconstitute-0281c | completed | worker-3 | 14635 leftover on disk; HOLD no View |
| 2026-09-10 03:04:05 JST | leftover-reconstitute-0284a | started | worker-1 | 13754/13965/14431 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:04:05 JST | leftover-reconstitute-0284b | started | worker-2 | 14104/14004 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:04:05 JST | leftover-reconstitute-0284c | started | worker-3 | 13754 --nf/--sw leftover; HOLD not PASS |
| 2026-09-10 03:04:39 JST | leftover-reconstitute-0284a | completed | worker-1 | 13754/13965/14431 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:04:39 JST | leftover-reconstitute-0284b | completed | worker-2 | 14104/14004 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:04:39 JST | leftover-reconstitute-0284c | completed | worker-3 | 13754 --nf/--sw leftover on disk; HOLD no View |
| 2026-09-10 03:04:39 JST | leftover-reconstitute-0287a | started | worker-1 | 14271/14476 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:04:39 JST | leftover-reconstitute-0287b | started | worker-2 | 13755/13957 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:04:39 JST | leftover-reconstitute-0287c | started | worker-3 | 13957b/14650b --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:05:14 JST | leftover-reconstitute-0287a | completed | worker-1 | 14271/14476 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:05:14 JST | leftover-reconstitute-0287b | completed | worker-2 | 13755/13957 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:05:14 JST | leftover-reconstitute-0287c | completed | worker-3 | 13957b/14650b --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:05:14 JST | leftover-reconstitute-0290a | started | worker-1 | 9703b/9703 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:05:14 JST | leftover-reconstitute-0290b | started | worker-2 | 14148/14613 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:05:14 JST | leftover-reconstitute-0290c | started | worker-3 | 11502 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:05:30 JST | leftover-reconstitute-0290a | started | worker-1 | 14807 setup.cfg [pytest] vs tox/ini/native leftover; HOLD not PASS |
| 2026-09-10 03:05:30 JST | leftover-reconstitute-0290b | started | worker-2 | 14807 pytest.ini [tool:pytest] vs pytest.cfg/tox leftover; HOLD not PASS |
| 2026-09-10 03:05:30 JST | leftover-reconstitute-0290c | started | worker-3 | 14807 -c toml native / -c ini [tool:pytest] vs pytest.cfg leftover; HOLD not PASS |
| 2026-09-10 03:05:30 JST | leftover-reconstitute-0290a | completed | worker-1 | 14807 setup.cfg [pytest]+tox/ini: 8.4.1 sibling wins / pytest9 Failed; +native/toml Failed all; HOLD no View |
| 2026-09-10 03:05:30 JST | leftover-reconstitute-0290b | completed | worker-2 | 14807 pytest.ini [tool:pytest] displaces tox.ini (default files); vs pytest.cfg default; HOLD no View |
| 2026-09-10 03:05:30 JST | leftover-reconstitute-0290c | completed | worker-3 | 14807 -c toml native vs pytest.cfg: 8.4.1 default / pytest9 native; -c ini [tool:pytest] ignored default; HOLD no View |
| 2026-09-10 03:05:50 JST | leftover-reconstitute-0290a | completed | worker-1 | 9703b/9703 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:05:50 JST | leftover-reconstitute-0290b | completed | worker-2 | 14148/14613 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:05:50 JST | leftover-reconstitute-0290c | completed | worker-3 | 11502 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:05:50 JST | leftover-reconstitute-0293a | started | worker-1 | 14696/13985 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:05:50 JST | leftover-reconstitute-0293b | started | worker-2 | 14253/14092 isolated --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:05:50 JST | leftover-reconstitute-0293c | started | worker-3 | 14705/14255 quoted --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:06:18 JST | leftover-reconstitute-0293a | completed | worker-1 | 14696/13985 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:06:18 JST | leftover-reconstitute-0293b | completed | worker-2 | 14253/14092 isolated --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:06:18 JST | leftover-reconstitute-0293c | completed | worker-3 | 14705/14255 quoted --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:06:18 JST | leftover-reconstitute-0296a | started | worker-1 | 14608c alt_inside --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:06:18 JST | leftover-reconstitute-0296b | started | worker-2 | 13913 tests/ --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:06:18 JST | leftover-reconstitute-0296c | started | worker-3 | 14514c/14431/13922/14084 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:07:00 JST | leftover-reconstitute-0296a | completed | worker-1 | 14608c alt_inside --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:07:00 JST | leftover-reconstitute-0296b | completed | worker-2 | 13913 tests/ --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:07:00 JST | leftover-reconstitute-0296c | completed | worker-3 | 14514c/14431/13922/14084 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:07:00 JST | leftover-reconstitute-0299a | started | worker-1 | 13882/14635 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:07:00 JST | leftover-reconstitute-0299b | started | worker-2 | 14683/14700 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:07:00 JST | leftover-reconstitute-0299c | started | worker-3 | 9298/14323 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:07:27 JST | leftover-reconstitute-0299a | completed | worker-1 | 13882/14635 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:07:27 JST | leftover-reconstitute-0299b | completed | worker-2 | 14683/14700 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:07:27 JST | leftover-reconstitute-0299c | completed | worker-3 | 9298/14323 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:07:27 JST | leftover-reconstitute-0302a | started | worker-1 | 14762/14051 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:07:27 JST | leftover-reconstitute-0302b | started | worker-2 | 14148/14613 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:07:27 JST | leftover-reconstitute-0302c | started | worker-3 | 14412/14004b --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:08:03 JST | leftover-reconstitute-0302a | completed | worker-1 | 14762/14051 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:08:03 JST | leftover-reconstitute-0302b | completed | worker-2 | 14148/14613 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:08:03 JST | leftover-reconstitute-0302c | completed | worker-3 | 14412/14004b --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:08:03 JST | leftover-reconstitute-0305a | started | worker-1 | 14271/14476 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:08:03 JST | leftover-reconstitute-0305b | started | worker-2 | 13755/13957 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:08:03 JST | leftover-reconstitute-0305c | started | worker-3 | 13957b/14650b --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:08:54 JST | leftover-reconstitute-0305a | completed | worker-1 | 14271/14476 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:08:54 JST | leftover-reconstitute-0305b | completed | worker-2 | 13755/13957 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:08:54 JST | leftover-reconstitute-0305c | completed | worker-3 | 13957b/14650b --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:08:54 JST | leftover-reconstitute-0308a | started | worker-1 | 13754/13965 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:08:54 JST | leftover-reconstitute-0308b | started | worker-2 | 14104/14004 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:08:54 JST | leftover-reconstitute-0308c | started | worker-3 | 14431/11502 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:09:21 JST | leftover-reconstitute-0308a | completed | worker-1 | 13754/13965 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:09:21 JST | leftover-reconstitute-0308b | completed | worker-2 | 14104/14004 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:09:21 JST | leftover-reconstitute-0308c | completed | worker-3 | 14431/11502 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:09:21 JST | leftover-reconstitute-0311a | started | worker-1 | 14608c/13913 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:09:21 JST | leftover-reconstitute-0311b | started | worker-2 | 14514c/14431 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:09:21 JST | leftover-reconstitute-0311c | started | worker-3 | 13922/14048 --maxfail leftover; HOLD not PASS |
| 2026-09-10 03:09:40 JST | leftover-reconstitute-0311a | completed | worker-1 | 14608c/13913 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:09:40 JST | leftover-reconstitute-0311b | completed | worker-2 | 14514c/14431 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:09:40 JST | leftover-reconstitute-0311c | completed | worker-3 | 13922/14048 --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:09:40 JST | leftover-reconstitute-0314a | started | worker-1 | next leftover reconstitution extras after leftover-0311; HOLD not PASS |
| 2026-09-10 03:10:23 JST | leftover-reconstitute-0314a | completed | worker-1 | 14253/14092/13985 isolated --maxfail leftover on disk; HOLD no View |
| 2026-09-10 03:10:23 JST | leftover-reconstitute-0317a | started | worker-1 | next leftover reconstitution extras after leftover-0314; HOLD not PASS |
| 2026-09-10 03:10:45 JST | leftover-reconstitute-0317a | completed | worker-1 | leftover-0317 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:10:45 JST | leftover-reconstitute-0320a | started | worker-1 | next leftover reconstitution extras after leftover-0317; HOLD not PASS |
| 2026-09-10 03:11:22 JST | leftover-reconstitute-0320a | completed | worker-1 | leftover-0320 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:11:22 JST | leftover-reconstitute-0323a | started | worker-1 | next leftover reconstitution extras after leftover-0320; HOLD not PASS |
| 2026-09-10 03:11:50 JST | leftover-reconstitute-0323a | completed | worker-1 | leftover-0323 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:11:50 JST | leftover-reconstitute-0326a | started | worker-1 | next leftover reconstitution extras after leftover-0323; HOLD not PASS |
| 2026-09-10 03:12:20 JST | leftover-reconstitute-0326a | completed | worker-1 | leftover-0326 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:12:20 JST | leftover-reconstitute-0329a | started | worker-1 | next leftover reconstitution extras after leftover-0326; HOLD not PASS |
| 2026-09-10 03:12:52 JST | leftover-reconstitute-0329a | completed | worker-1 | leftover-0329 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:12:52 JST | leftover-reconstitute-0332a | started | worker-1 | next leftover reconstitution extras after leftover-0329; HOLD not PASS |
| 2026-09-10 03:13:19 JST | leftover-reconstitute-0332a | completed | worker-1 | leftover-0332 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:13:19 JST | leftover-reconstitute-0335a | started | worker-1 | next leftover reconstitution extras after leftover-0332; HOLD not PASS |
| 2026-09-10 03:13:42 JST | leftover-reconstitute-0335a | completed | worker-1 | leftover-0335 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:13:42 JST | leftover-reconstitute-0338a | started | worker-1 | next leftover reconstitution extras after leftover-0335; HOLD not PASS |
| 2026-09-10 03:14:23 JST | leftover-reconstitute-0338a | completed | worker-1 | leftover-0338 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:14:23 JST | leftover-reconstitute-0341a | started | worker-1 | next leftover reconstitution extras after leftover-0338; HOLD not PASS |
| 2026-09-10 03:14:51 JST | leftover-reconstitute-0341a | completed | worker-1 | leftover-0341 --maxfail extras on disk; HOLD no View |
| 2026-09-10 03:14:51 JST | leftover-reconstitute-0344a | started | worker-1 | next leftover reconstitution extras after leftover-0341; HOLD not PASS |
| 2026-09-10 03:16:26 JST | leftover-reconstitute-0344a | completed | worker-1 | leftover-0344 --maxfail extras on disk; HOLD no View. Next leftover extras immediately. |
| 2026-09-10 03:16:51 JST | leftover-reconstitute-0347a | started | worker-1 | 14807 setup.cfg [pytest] vs pytest.cfg / -c ini leftover; HOLD not PASS |
| 2026-09-10 03:16:51 JST | leftover-reconstitute-0347b | started | worker-2 | 14807 pytest.ini [tool:pytest] vs native/ini_options leftover; HOLD not PASS |
| 2026-09-10 03:16:51 JST | leftover-reconstitute-0347c | started | worker-3 | 14807 -c toml vs setup.cfg [pytest]; tox [tool:pytest] vs pytest.ini leftover; HOLD not PASS |
| 2026-09-10 03:17:43 JST | leftover-reconstitute-0347a | completed | worker-1 | 14807 setup.cfg [pytest] vs pytest.cfg Failed all; -c ini suppresses Failed only_cini all; HOLD no View |
| 2026-09-10 03:17:43 JST | leftover-reconstitute-0347b | completed | worker-2 | 14807 pytest.ini [tool:pytest] displaces native/ini_options (default files); tox [tool:pytest] loses to pytest.ini; HOLD no View |
| 2026-09-10 03:17:43 JST | leftover-reconstitute-0347c | completed | worker-3 | 14807 -c toml suppresses setup.cfg [pytest] Failed; unread default / native 8.4.1 default pytest9 native; ini_options suppresses Failed on 8.4.1 only; HOLD no View |
| 2026-09-10 03:19:55 JST | leftover-reconstitute-0347a | completed | worker-1 | 14807 setup.cfg [pytest] vs pytest.cfg Failed all; -c ini displaces Failed only_cini; HOLD no View |
| 2026-09-10 03:19:55 JST | leftover-reconstitute-0347b | completed | worker-2 | 14807 pytest.ini [tool:pytest] vs native/ini_options test_default all (filename displaces pyproject); setup.cfg [pytest] vs ini_options 8.4.1 only_iniopt / pytest9 Failed; HOLD no View |
| 2026-09-10 03:19:55 JST | leftover-reconstitute-0347c | completed | worker-3 | 14807 -c toml unread displaces setup.cfg [pytest] Failed (default files); -c native 8.4.1 default / pytest9 only_native; tox [tool:pytest] vs pytest.ini only_ini; HOLD no View |
| 2026-09-10 03:19:55 JST | leftover-reconstitute-0350a | started | worker-1 | 3062 live-log pytest.ini/pyproject/tox leftover; HOLD not PASS |
| 2026-09-10 03:19:55 JST | leftover-reconstitute-0350b | started | worker-2 | 14807 leftover remaining collect pairings; HOLD not PASS |
| 2026-09-10 03:21:23 JST | leftover-reconstitute-0350a | completed | worker-1 | 3062 getini keeps %% on pytest.ini/pyproject; tox [pytest] raw format; HOLD no View |
| 2026-09-10 03:21:23 JST | leftover-reconstitute-0350b | completed | worker-2 | 14807 --config-file=/dev/null displaces cwd pytest.ini/native/setup.cfg (test_default); tox [tool:pytest] ignored; HOLD no View |
| 2026-09-10 03:21:23 JST | leftover-reconstitute-0353a | started | worker-1 | 3062 live-log -s leftover; HOLD not PASS |
| 2026-09-10 03:22:03 JST | leftover-reconstitute-0353a | completed | worker-1 | 3062 setup.cfg fully escaped live-log ValueError %W; pytest.ini/pyproject -s 1 pass no live log print; HOLD no View |
| 2026-09-10 03:22:03 JST | leftover-reconstitute-0356a | started | worker-1 | 3062 --log-cli leftover; HOLD not PASS |
| 2026-09-10 03:22:45 JST | leftover-reconstitute-0356a | completed | worker-1 | 3062 --log-cli unrecognized rc=4 all versions; HOLD no View |
| 2026-09-10 03:22:45 JST | leftover-reconstitute-0359a | started | worker-1 | 3062 -o log_cli=true leftover; HOLD not PASS |
| 2026-09-10 03:23:33 JST | leftover-reconstitute-0359a | completed | worker-1 | 3062 -o log_cli=true without -s still no live log print; HOLD no View |
| 2026-09-10 03:23:33 JST | leftover-reconstitute-0362a | started | worker-1 | 3062 -s -o log_cli=true leftover; HOLD not PASS |
| 2026-09-10 03:24:16 JST | leftover-reconstitute-0362a | completed | worker-1 | 3062 pytest.ini/pyproject log_cli=true even with -s -o log_cli=true does not print live log; setup.cfg [tool:pytest] does; HOLD no View |
| 2026-09-10 03:24:16 JST | leftover-reconstitute-0365a | started | worker-1 | 14807 -o python_files vs cwd configs leftover; HOLD not PASS |
| 2026-09-10 03:25:28 JST | leftover-reconstitute-0365a | completed | worker-1 | 14807 -o python_files replaces cwd python_files (rc=5 if that file is absent); beats pytest.ini+native and setup.cfg+native; HOLD no View |
| 2026-09-10 03:25:28 JST | leftover-reconstitute-0368a | started | worker-1 | next unused leftover reconstitution after leftover-0365; HOLD not PASS |
| 2026-09-10 03:29:35 JST | leftover-reconstitute-0371a | started | worker-1 | 14807 PYTEST_ADDOPTS python_files vs setup.cfg/tox/pytest.cfg leftover; HOLD not PASS |
| 2026-09-10 03:32:52 JST | leftover-reconstitute-0371a | completed | worker-1 | 14807 PYTEST_ADDOPTS -o python_files=only_native.py replaces tox/ini/cfg/native/toml files; does NOT suppress setup.cfg [pytest] Failed; HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0368a | completed | worker-1 | 14807 PYTEST_ADDOPTS python_files vs cwd pytest.ini/native: rc=5 if that file is absent (same as CLI -o); vs pytest.ini+native only_native all; HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0374a | started | worker-1 | 14807 --override-ini python_files / restore test_*.py / env vs -c leftover; HOLD not PASS |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0374a | completed | worker-1 | 14807 --override-ini python_files same as CLI -o; -o python_files=test_*.py restores test_default; PYTEST_ADDOPTS still applies with --config-file=/dev/null and beats -c custom.ini; HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0377a | started | worker-1 | 3062 --log-cli-format leftover; HOLD not PASS |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0377a | completed | worker-1 | 3062 --log-cli-format CLI overrides setup.cfg live-log (CLI:test_log.py:3 hello-log); pytest.ini/pyproject still no live-log; HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0380a | started | worker-1 | 14807 CLI -o vs PYTEST_ADDOPTS python_files leftover; HOLD not PASS |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0380a | completed | worker-1 | 14807 CLI -o python_files and --override-ini win over PYTEST_ADDOPTS; -o python_files=test_*.py restores test_default vs setup.cfg/tox/native; HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0383a | started | worker-1 | 3062 --log-file leftover; HOLD not PASS |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0383a | completed | worker-1 | 3062 --log-file writes setup.cfg live-log line; pytest.ini/pyproject --log-file empty (same split as live-log); HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0386a | started | worker-1 | 3062 --log-file-format leftover; HOLD not PASS |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0386a | completed | worker-1 | 3062 --log-file-format FILE: prefix on setup.cfg; pytest.ini --log-file-level=DEBUG still empty; PYTEST_ADDOPTS python_files=test_*.py restores test_default; HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0389a | started | worker-1 | 3062 --log-cli-date-format leftover; HOLD not PASS |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0389a | completed | worker-1 | 3062 --log-cli-date-format without asctime does not add timestamp; setup.cfg live-log still prints; HOLD no View |
| 2026-09-10 03:35:57 JST | leftover-reconstitute-0392a | started | worker-1 | 3062 -o log_format/log_cli_format leftover; HOLD not PASS |
| 2026-09-10 03:36:43 JST | leftover-reconstitute-0392a | completed | worker-1 | 3062 -o log_format and -o log_cli_format override setup.cfg live-log; asctime+date-format prints HH:MM:SS; pytest.ini -o log_cli_format still no live-log; HOLD no View |
| 2026-09-10 03:36:43 JST | leftover-reconstitute-0395a | started | worker-1 | 14807 -o addopts / 3062 -o log_cli_level leftover; HOLD not PASS |
| 2026-09-10 03:37:27 JST | leftover-reconstitute-0395a | completed | worker-1 | 14807 -o addopts=-q is additive quiet not python_files replace; 3062 -o log_cli_level=WARNING live-log on setup.cfg only; pytest.ini still no live-log; HOLD no View |
| 2026-09-10 03:37:27 JST | leftover-reconstitute-0398a | started | worker-1 | 14807 -o addopts vs setup.cfg / 3062 -o log_date_format leftover; HOLD not PASS |
| 2026-09-10 03:38:24 JST | leftover-reconstitute-0398a | completed | worker-1 | 14807 -o addopts=-q vs setup.cfg still only_cfg (addopts does not replace python_files); PYTEST_ADDOPTS python_files=test_*.py restores test_default; 3062 -o log_date_format with asctime prints HH:MM:SS; HOLD no View |
| 2026-09-10 03:38:24 JST | leftover-reconstitute-0401a | started | worker-1 | 14807 --override-ini addopts / 3062 -o log_cli_date_format leftover; HOLD not PASS |
| 2026-09-10 03:39:42 JST | leftover-reconstitute-0401a | completed | worker-1 | 14807 --override-ini addopts=-q additive quiet (only_ini); -o addopts=-q vs native 8.4.1 test_default / pytest9 only_native; 3062 -o log_cli_date_format with asctime prints HH:MM:SS hello-log; HOLD no View |
| 2026-09-10 03:39:42 JST | leftover-reconstitute-0404a | started | worker-1 | 14807 -o addopts vs ignored table / 3062 --log-file-date-format leftover; HOLD not PASS |
| 2026-09-10 03:40:22 JST | leftover-reconstitute-0404a | completed | worker-1 | 14807 -o addopts=-q vs ignored pytest.ini table test_default quiet; env addopts vs native 8.4.1 default / pytest9 only_native; 3062 --log-file-date-format with asctime writes HH:MM:SS; HOLD no View |
| 2026-09-10 03:40:22 JST | leftover-reconstitute-0407a | started | worker-1 | 14807 -o addopts vs pytest.cfg / -o pythonpath leftover; HOLD not PASS |
| 2026-09-10 03:41:01 JST | leftover-reconstitute-0407a | completed | worker-1 | 14807 -o addopts=-q vs pytest.cfg test_default quiet; -o pythonpath=. does not replace python_files (only_ini); 3062 pytest.ini -o log_cli_date_format still no live-log; HOLD no View |
| 2026-09-10 03:41:01 JST | leftover-reconstitute-0410a | started | worker-1 | 14807 python_files restore + addopts=-q leftover; HOLD not PASS |
| 2026-09-10 03:41:14 JST | leftover-reconstitute-0410a | completed | worker-1 | 14807 -o python_files=test_*.py -o addopts=-q restores test_default quiet vs pytest.ini/setup.cfg; -o pythonpath=. vs native does not replace python_files; HOLD no View |
| 2026-09-10 03:41:14 JST | leftover-reconstitute-0413a | started | worker-1 | 14807 -o minversion=99 / restore vs pytest.cfg leftover; HOLD not PASS |
| 2026-09-10 03:41:50 JST | leftover-reconstitute-0413a | completed | worker-1 | 14807 -o minversion=99: 8.4.1 still only_ini (not enforced); pytest 9 rc=4 requires pytest-99 citing pytest.ini; restore test_*.py vs pytest.cfg/ignored table test_default; HOLD no View |
| 2026-09-10 03:41:50 JST | leftover-reconstitute-0416a | started | worker-1 | 14807 -o minversion=99 vs native/setup.cfg leftover; HOLD not PASS |
| 2026-09-10 03:42:24 JST | leftover-reconstitute-0416a | completed | worker-1 | 14807 -o minversion=99 vs native/setup.cfg/env/override-ini: 8.4.1 still collects; pytest 9 rc=4 citing cwd config file; HOLD no View |
| 2026-09-10 03:42:24 JST | leftover-reconstitute-0419a | started | worker-1 | 14807 -o minversion=99 vs pytest.cfg /dev/null -c leftover; HOLD not PASS |
| 2026-09-10 03:42:52 JST | leftover-reconstitute-0419a | completed | worker-1 | 14807 -o minversion=99: pytest.cfg error None:; /dev/null cites /dev/null; -c cites custom.ini; 8.4.1 still collects; minversion=8.0 all pass; HOLD no View |
| 2026-09-10 03:42:52 JST | leftover-reconstitute-0422a | started | worker-1 | 14807 -o minversion=9.0/9.1 leftover; HOLD not PASS |
| 2026-09-10 03:43:56 JST | leftover-reconstitute-0422a | completed | worker-1 | 14807 -o minversion=9.0 all pass including 8.4.1 (not enforced); minversion=9.1/9.1.0 8.4.1 still collects / 9.0.1-9.0.3 rc=4 / 9.1.0+ pass; HOLD no View |
| 2026-09-10 03:43:56 JST | leftover-reconstitute-0425a | started | worker-1 | 14807 last -o minversion leftover; HOLD not PASS |
| 2026-09-10 03:45:00 JST | leftover-reconstitute-0425a | completed | worker-1 | 14807 last -o minversion wins (99 then 8.0 all pass; 8.0 then 99 pytest9 rc=4 / 8.4.1 still collects); bare minversion=9 all pass; HOLD no View |
| 2026-09-10 03:45:00 JST | leftover-reconstitute-0428a | started | worker-1 | 14807 -o minversion=9.0.2 / env vs CLI leftover; HOLD not PASS |
| 2026-09-10 03:45:42 JST | leftover-reconstitute-0428a | completed | worker-1 | 14807 -o minversion=9.0.2: 8.4.1 still collects / 9.0.1 rc=4 / 9.0.3+ pass; CLI minversion wins over PYTEST_ADDOPTS; HOLD no View |
| 2026-09-10 03:45:42 JST | leftover-reconstitute-0431a | started | worker-1 | 14807 -o minversion=9.0.3/9.1.1 leftover; HOLD not PASS |
| 2026-09-10 03:46:26 JST | leftover-reconstitute-0431a | completed | worker-1 | 14807 -o minversion=9.0.3: 8.4.1 still collects / 9.0.1 rc=4 / 9.0.3+ pass; minversion=9.1.1 only 9.1.1 pass; --override-ini 9.0.2 same as -o; HOLD no View |
| 2026-09-10 03:46:26 JST | leftover-reconstitute-0434a | started | worker-1 | 14807 -o minversion=9.0.1/9.1.0 leftover; HOLD not PASS |
| 2026-09-10 03:47:13 JST | leftover-reconstitute-0434a | completed | worker-1 | 14807 -o minversion=9.0.1 all pass including 8.4.1; minversion=9.1.0 8.4.1 still collects / 9.0.1-9.0.3 rc=4 / 9.1.0+ pass; --override-ini 8.0 wins over env 99; HOLD no View |
| 2026-09-10 03:47:13 JST | leftover-reconstitute-0437a | started | worker-1 | 14807 -o minversion=9.0.1 vs native leftover; HOLD not PASS |
| 2026-09-10 03:47:54 JST | leftover-reconstitute-0437a | completed | worker-1 | 14807 -o minversion=9.0.1 vs native 8.4.1 test_default / pytest9 only_native; --override-ini 9.1.1 only 9.1.1 pass; setup.cfg minversion=9.0.2 9.0.1 rc=4; HOLD no View |
| 2026-09-10 03:47:54 JST | leftover-reconstitute-0440a | started | worker-1 | 14807 -o minversion=9.0.1 vs setup.cfg leftover; HOLD not PASS |
| 2026-09-10 03:48:16 JST | leftover-reconstitute-0440a | completed | worker-1 | 14807 -o minversion=9.0.1 vs setup.cfg all collect (8.4.1 unread enforce / pytest9 satisfied); env minversion=9.0.2 9.0.1 rc=4; pytest.cfg minversion=9.1.1 None: on pytest9 except 9.1.1; HOLD no View |
| 2026-09-10 03:48:17 JST | leftover-reconstitute-0443a | started | worker-1 | next unused leftover reconstitution after leftover-0440; HOLD not PASS |
| 2026-09-10 03:48:45 JST | leftover-reconstitute-0443a | completed | worker-1 | 14807 -o minversion=9.0.3 vs native 8.4.1 default / 9.0.1 rc=4 / 9.0.3+ only_native; env 9.1.1 only 9.1.1 pass; -c custom.ini minversion=9.0.2 9.0.1 rc=4 citing custom.ini; HOLD no View |
| 2026-09-10 03:48:45 JST | leftover-reconstitute-0446a | started | worker-1 | next unused leftover reconstitution after leftover-0443; HOLD not PASS |
| 2026-09-10 03:49:11 JST | leftover-reconstitute-0446a | completed | worker-1 | 14807 /dev/null -o minversion=9.1.1 cites /dev/null on pytest9 except 9.1.1; setup.cfg 9.0.3 9.0.1 rc=4; env 9.1.1 vs native only 9.1.1 pass; HOLD no View |
| 2026-09-10 03:49:11 JST | leftover-reconstitute-0449a | started | worker-1 | next unused leftover reconstitution after leftover-0446; HOLD not PASS |
| 2026-09-10 03:49:41 JST | leftover-reconstitute-0449a | completed | worker-1 | 14807 -o minversion=9.1 vs tox.ini 8.4.1 only_tox / 9.0.1-9.0.3 rc=4 / 9.1.0+ only_tox; -c 9.1.1 only 9.1.1 pass citing custom.ini; minversion=9.0.1 + python_files=test_*.py restores test_default all; HOLD no View |
| 2026-09-10 03:49:41 JST | leftover-reconstitute-0452a | started | worker-1 | next unused leftover reconstitution after leftover-0449; HOLD not PASS |
| 2026-09-10 03:52:00 JST | leftover-reconstitute-0452a | completed | worker-1 | 14807 -o minversion=9.1.1 vs tox.ini 8.4.1 only_tox / 9.0.1-9.1.0 rc=4 / 9.1.1 only_tox; minversion=9.0.1 + python_files=test_*.py restores test_default vs setup.cfg/native; HOLD no View |
| 2026-09-10 03:52:00 JST | leftover-reconstitute-0455a | started | worker-1 | 14807 minversion restore vs tox / 9.1.1 vs setup.cfg leftover; HOLD not PASS |
| 2026-09-10 03:52:14 JST | leftover-reconstitute-0455a | completed | worker-1 | 14807 minversion=9.0.1 + python_files restore vs tox test_default all; minversion=9.1.1 vs setup.cfg only 9.1.1 pass; vs ignored pytest.ini table 8.4.1 default / 9.0.1-9.0.3 rc=4 / 9.1.0+ default; HOLD no View |
| 2026-09-10 03:52:14 JST | leftover-reconstitute-0458a | started | worker-1 | 14101 -o xfail_strict / 14807 empty_parameter_set_mark leftover; HOLD not PASS |
| 2026-09-10 03:53:05 JST | leftover-reconstitute-0458a | completed | worker-1 | 14101 -o xfail_strict=true collect-only 2 tests all (XPASS is execute); empty_parameter_set_mark/consider_namespace_packages do not replace python_files (only_ini); HOLD no View |
| 2026-09-10 03:53:05 JST | leftover-reconstitute-0461a | started | worker-1 | 14101 -o xfail_strict run leftover; HOLD not PASS |
| 2026-09-10 03:53:40 JST | leftover-reconstitute-0461a | completed | worker-1 | 14101 -o xfail_strict=true run: 8.4.1 xE rc=1; pytest 9 uFuF XPASS-as-fail rc=1; faulthandler_timeout/python_classes do not replace python_files; HOLD no View |
| 2026-09-10 03:53:40 JST | leftover-reconstitute-0464a | started | worker-1 | 14807 console_output_style / 3062 log_file_level leftover; HOLD not PASS |
| 2026-09-10 03:54:13 JST | leftover-reconstitute-0464a | completed | worker-1 | 14807 -o console_output_style=classic collect only_ini; -o verbosity=2 pytest9 warning still only_ini; 3062 -o log_file_level=WARNING still setup.cfg live-log; HOLD no View |
| 2026-09-10 03:54:13 JST | leftover-reconstitute-0467a | started | worker-1 | 3062 -o log_file leftover; HOLD not PASS |
| 2026-09-10 03:54:44 JST | leftover-reconstitute-0467a | completed | worker-1 | 3062 -o log_file vs pytest.ini still empty; -o disable_test_id_escaping collect only_ini; -o strict=true collect only_ini; HOLD no View |
| 2026-09-10 03:54:44 JST | leftover-reconstitute-0470a | started | worker-1 | 14807 --strict-config -o verbosity leftover; HOLD not PASS |
| 2026-09-10 03:55:12 JST | leftover-reconstitute-0473a | started | worker-1 | 14807 named toml/Failed/tox minversion leftover; HOLD not PASS |
| 2026-09-10 03:55:12 JST | leftover-reconstitute-0473a | completed | worker-1 | 14807 named pytest.toml -o minversion=9.0.1: 8.4.1 test_default / pytest9 only_pytest_toml; minversion=9.1.1 only 9.1.1 pass citing pytest.toml; minversion=99 pytest9 rc=4 citing pytest.toml; setup.cfg [pytest] Failed first vs -o minversion=99/9.0.1 (does not suppress Failed); tox.ini minversion=9.0.1 only_tox all; minversion=9.0.3 9.0.1 rc=4 citing tox.ini; pytest.ini [tool:pytest] minversion=99 cites pytest.ini; env minversion=9.0.1 vs named toml same as CLI; HOLD no View |
| 2026-09-10 03:55:37 JST | leftover-reconstitute-0470a | completed | worker-1 | 14807 --strict-config -o verbosity=2: 8.4.1 rc=0 only_ini; pytest 9 rc=4 unknown verbosity; strict_markers collect only_ini; 14101 -o strict_xfail same xE/uFuF; HOLD no View |
| 2026-09-10 03:55:37 JST | leftover-reconstitute-0473a | started | worker-1 | 14807 --strict-config python_files/minversion leftover; HOLD not PASS |
| 2026-09-10 03:56:39 JST | leftover-reconstitute-0473a | completed | worker-1 | 14807 --strict-config -o python_files known option all pass; --strict-config -o minversion=99 8.4.1 still collects / pytest9 rc=4; --strict-config -o verbosity=2 vs native 8.4.1 default / pytest9 rc=4 unknown; HOLD no View |
| 2026-09-10 03:56:39 JST | leftover-reconstitute-0476a | started | worker-1 | 14807 -o addopts=--strict-config + verbosity leftover; HOLD not PASS |
| 2026-09-10 03:57:34 JST | leftover-reconstitute-0476a | completed | worker-1 | 14807 -o addopts=--strict-config -o verbosity=2: 8.4.1/9.0.1/9.0.3 rc=0 (9.x warning); 9.1.0+ rc=4; CLI --strict-config and PYTEST_ADDOPTS=--strict-config pytest9 rc=4 all; HOLD no View |
| 2026-09-10 03:57:34 JST | leftover-reconstitute-0479a | started | worker-1 | 14807 addopts=--strict-config verbosity vs native leftover; HOLD not PASS |
| 2026-09-10 03:58:17 JST | leftover-reconstitute-0479a | completed | worker-1 | 14807 addopts=--strict-config verbosity vs native same 9.0.x warning / 9.1.0+ rc=4; --strict-markers does not make verbosity fatal; --strict-config console_output_style known all pass; HOLD no View |
| 2026-09-10 03:58:17 JST | leftover-reconstitute-0482a | started | worker-1 | 14807 --strict-config verbosity vs setup.cfg leftover; HOLD not PASS |
| 2026-09-10 03:58:42 JST | leftover-reconstitute-0482a | completed | worker-1 | 14807 --strict-config -o verbosity=2 vs setup.cfg 8.4.1 rc=0 / pytest9 rc=4; addopts=--strict-config vs pytest.cfg 9.0.x warning / 9.1.0+ rc=4; --strict-config pythonpath known all pass; HOLD no View |
| 2026-09-10 03:58:42 JST | leftover-reconstitute-0485a | started | worker-1 | next unused leftover reconstitution after leftover-0482; HOLD not PASS |
| 2026-09-10 03:59:30 JST | leftover-reconstitute-0485a | completed | worker-1 | 14807 --strict-config -o verbosity=2 vs tox.ini 8.4.1 rc=0 / pytest9 rc=4; PYTEST_ADDOPTS=--strict-config vs native verbosity pytest9 rc=4; --strict-config faulthandler_timeout known all pass; HOLD no View |
| 2026-09-10 03:59:30 JST | leftover-reconstitute-0488a | started | worker-1 | next unused leftover reconstitution after leftover-0485; HOLD not PASS |
| 2026-09-10 04:01:54 JST | leftover-reconstitute-0488a | completed | worker-1 | 14807 --strict-config -o verbosity=2 vs named pytest.toml/ignored pytest.ini/-c custom.ini: 8.4.1 collects (test_default/only_cini) / pytest9 rc=4 unknown verbosity; setup.cfg [pytest] Failed first vs --strict-config verbosity (does not reach unknown option); --strict-config --override-ini verbosity=2 same as CLI -o; PYTEST_ADDOPTS=--strict-config vs named toml verbosity pytest9 rc=4; --strict-config -o minversion=99 vs named toml 8.4.1 test_default / pytest9 rc=4 citing pytest.toml; --strict-config -o python_files=only_pytest_toml.py only_pytest_toml all including 8.4.1; HOLD no View |
| 2026-09-10 04:02:28 JST | leftover-reconstitute-0491a | started | worker-1 | 14807 addopts=--strict-config verbosity vs tox/setup.cfg leftover; HOLD not PASS |
| 2026-09-10 04:02:45 JST | leftover-reconstitute-0491a | completed | worker-1 | 14807 addopts=--strict-config verbosity vs tox/setup.cfg/ignored table: 8.4.1/9.0.1/9.0.3 rc=0 9.1.0+ rc=4; CLI --strict-config vs ignored table pytest9 rc=4; empty_parameter_set_mark/consider_namespace_packages known all pass; HOLD no View |
| 2026-09-10 04:02:45 JST | leftover-reconstitute-0494a | started | worker-1 | 14101 --strict-config xfail_strict / 3062 --strict-config log_cli leftover; HOLD not PASS |
| 2026-09-10 04:03:31 JST | leftover-reconstitute-0494a | completed | worker-1 | 14101 --strict-config -o xfail_strict same 8.4.1 xE / pytest9 XPASS-as-fail; -o filterwarnings=error collect only_ini; 3062 --strict-config -o log_cli=true vs pytest.ini still no live-log; HOLD no View |
| 2026-09-10 04:03:31 JST | leftover-reconstitute-0497a | started | worker-1 | 14807 --strict-config filterwarnings / python_files restore leftover; HOLD not PASS |
| 2026-09-10 04:03:48 JST | leftover-reconstitute-0497a | completed | worker-1 | 14807 --strict-config -o filterwarnings=error collect only_ini; 3062 addopts=--strict-config log_cli vs pytest.ini still no live-log; --strict-config python_files=test_*.py restores test_default; HOLD no View |
| 2026-09-10 04:03:48 JST | leftover-reconstitute-0500a | started | worker-1 | 3062 --strict-config log_cli vs setup.cfg leftover; HOLD not PASS |
| 2026-09-10 04:04:37 JST | leftover-reconstitute-0500a | completed | worker-1 | 3062 --strict-config -o log_cli=true vs setup.cfg still live-log; --strict-config python_files restore vs tox test_default; usefixtures known all pass; HOLD no View |
| 2026-09-10 04:04:37 JST | leftover-reconstitute-0503a | started | worker-1 | 14807 --strict-config python_files restore vs setup.cfg/native leftover; HOLD not PASS |
| 2026-09-10 04:05:30 JST | leftover-reconstitute-0503a | completed | worker-1 | 14807 --strict-config python_files=test_*.py restores test_default vs setup.cfg/native; norecursedirs=.* still only_ini; HOLD no View |
| 2026-09-10 04:05:30 JST | leftover-reconstitute-0506a | started | worker-1 | 14807 --strict-config python_files restore vs ignored table leftover; HOLD not PASS |
| 2026-09-10 04:06:16 JST | leftover-reconstitute-0506a | completed | worker-1 | 14807 --strict-config python_files restore vs ignored table/pytest.cfg test_default; --strict-config testpaths=. still only_ini; HOLD no View |
| 2026-09-10 04:06:16 JST | leftover-reconstitute-0509a | started | worker-1 | next unused leftover reconstitution after leftover-0506; HOLD not PASS |
| 2026-09-10 04:06:50 JST | leftover-reconstitute-0509a | completed | worker-1 | 14807 --strict-config python_files restore vs named toml/custom.ini test_default; python_functions=test_ok still only_ini; HOLD no View |
| 2026-09-10 04:06:50 JST | leftover-reconstitute-0512a | started | worker-1 | next unused leftover reconstitution after leftover-0509; HOLD not PASS |
| 2026-09-10 04:09:53 JST | leftover-reconstitute-0512a | completed | worker-1 | 14807 --strict-config python_files=test_*.py vs setup.cfg [pytest] Failed all (does not suppress); python_classes=Test* still only_ini; /dev/null --strict-config python_files=test_*.py collects test_ok.py; HOLD no View |
| 2026-09-10 04:09:53 JST | leftover-reconstitute-0515a | started | worker-1 | 14807 --strict-config vs Failed / env restore leftover; HOLD not PASS |
| 2026-09-10 04:10:21 JST | leftover-reconstitute-0515a | completed | worker-1 | 14807 --strict-config vs setup.cfg [pytest]+pytest.cfg Failed all; PYTEST_ADDOPTS python_files restore does not suppress Failed; --import-mode=importlib still only_ini; HOLD no View |
| 2026-09-10 04:10:21 JST | leftover-reconstitute-0518a | started | worker-1 | 14807 -o python_files vs Failed / --strict-config -c leftover; HOLD not PASS |
| 2026-09-10 04:10:52 JST | leftover-reconstitute-0518a | completed | worker-1 | 14807 -o python_files and PYTEST_ADDOPTS do not suppress setup.cfg [pytest] Failed; --strict-config -c custom.ini suppresses Failed (rc=5 no only_cini.py in that tree); HOLD no View |
| 2026-09-10 04:10:52 JST | leftover-reconstitute-0521a | started | worker-1 | 14807 --config-file=/dev/null vs Failed leftover; HOLD not PASS |
| 2026-09-10 04:11:52 JST | leftover-reconstitute-0521a | completed | worker-1 | 14807 --config-file=/dev/null vs setup.cfg [pytest] Failed: test_default all (displaces Failed); --strict-config /dev/null same; /dev/null + python_files=test_*.py test_default; HOLD no View |
| 2026-09-10 04:11:52 JST | leftover-reconstitute-0524a | started | worker-1 | 14807 /dev/null python_files=only_cfg vs Failed leftover; HOLD not PASS |
| 2026-09-10 04:12:24 JST | leftover-reconstitute-0524a | completed | worker-1 | 14807 /dev/null -o python_files=only_cfg.py vs Failed: only_cfg all; -c custom.ini vs Failed tree with only_cini.py: only_cini all; --noconftest still Failed; HOLD no View |
| 2026-09-10 04:12:24 JST | leftover-reconstitute-0527a | started | worker-1 | 14807 --override-ini vs Failed / env --config-file=/dev/null leftover; HOLD not PASS |
| 2026-09-10 04:12:50 JST | leftover-reconstitute-0527a | completed | worker-1 | 14807 --override-ini python_files still Failed; -c + python_files=test_*.py restores test_default (suppresses Failed); PYTEST_ADDOPTS=--config-file=/dev/null displaces Failed test_default; HOLD no View |
| 2026-09-10 04:12:50 JST | leftover-reconstitute-0530a | started | worker-1 | next unused leftover reconstitution after leftover-0527; HOLD not PASS |
| 2026-09-10 04:13:40 JST | leftover-reconstitute-0530a | completed | worker-1 | 14807 PYTEST_ADDOPTS=-c custom.ini vs Failed: rc=5 (only_cini absent) / suppresses Failed; --strict-config /dev/null only_cfg.py: only_cfg all; /dev/null vs pytest.cfg+Failed: test_default; HOLD no View |
| 2026-09-10 04:13:40 JST | leftover-reconstitute-0533a | started | worker-1 | next unused leftover reconstitution after leftover-0530; HOLD not PASS |
| 2026-09-10 04:16:02 JST | leftover-reconstitute-0533a | completed | worker-1 | 14807 PYTEST_ADDOPTS=-c custom.ini vs Failed with only_cini.py present: only_cini all (suppresses Failed); --strict-config -c custom.ini -o verbosity=2: 8.4.1 only_cini / pytest9 rc=4 unknown verbosity (Failed suppressed then unknown option); --strict-config -c minversion=99 cites custom.ini; -c + --override-ini python_files=test_*.py restores test_default; --strict-config -c unread TOML vs Failed test_default all; -c native TOML 8.4.1 default / pytest9 only_native; env -c native same as CLI; HOLD no View |
| 2026-09-10 04:16:39 JST | leftover-reconstitute-0536a | started | worker-1 | 14807 env -c + python_files restore / -c /dev/null / override-ini only_cfg vs Failed leftover; HOLD not PASS |
| 2026-09-10 04:17:11 JST | leftover-reconstitute-0536a | completed | worker-1 | 14807 env -c custom.ini -o python_files=test_*.py vs Failed: test_default all; -c /dev/null vs Failed: test_default all; --override-ini python_files=only_cfg.py still Failed; HOLD no View |
| 2026-09-10 04:17:11 JST | leftover-reconstitute-0539a | started | worker-1 | 14807 -c /dev/null vs Failed+pytest.cfg leftover; HOLD not PASS |
| 2026-09-10 04:17:44 JST | leftover-reconstitute-0539a | completed | worker-1 | 14807 -c /dev/null vs Failed+pytest.cfg: test_default all; env -c /dev/null -o python_files=only_cfg.py: only_cfg all; --override-ini + --strict-config still Failed; HOLD no View |
| 2026-09-10 04:17:44 JST | leftover-reconstitute-0542a | started | worker-1 | 14807 CLI -c /dev/null -o only_cfg leftover; HOLD not PASS |
| 2026-09-10 04:18:47 JST | leftover-reconstitute-0542a | completed | worker-1 | 14807 -c /dev/null -o python_files=only_cfg.py: only_cfg all; PYTEST_ADDOPTS=-c /dev/null and --strict-config -c /dev/null: test_default (displaces Failed); HOLD no View |
| 2026-09-10 04:18:47 JST | leftover-reconstitute-0545a | started | worker-1 | 14807 -c /dev/null vs native/ini/tox leftover; HOLD not PASS |
| 2026-09-10 04:19:44 JST | leftover-reconstitute-0545a | completed | worker-1 | 14807 -c /dev/null vs native/ini/tox: test_default all (displaces cwd python_files); HOLD no View |
| 2026-09-10 04:19:44 JST | leftover-reconstitute-0548a | started | worker-1 | 14807 -c /dev/null vs setup.cfg tool:pytest leftover; HOLD not PASS |
| 2026-09-10 04:20:09 JST | leftover-reconstitute-0548a | completed | worker-1 | 14807 -c /dev/null vs setup.cfg [tool:pytest]/pytest.cfg/pytest.ini: test_default all; -c /dev/null -o python_files=test_*.py vs pytest.ini test_default; HOLD no View |
| 2026-09-10 04:20:09 JST | leftover-reconstitute-0551a | started | worker-1 | next unused leftover reconstitution after leftover-0548; HOLD not PASS |
| 2026-09-10 04:21:04 JST | leftover-reconstitute-0551a | completed | worker-1 | 14807 -c /dev/null vs named toml/ignored table: test_default all; -c /dev/null -o python_files=only_ini.py vs pytest.ini: only_ini all; HOLD no View |
| 2026-09-10 04:21:04 JST | leftover-reconstitute-0554a | started | worker-1 | next unused leftover reconstitution after leftover-0551; HOLD not PASS |
| 2026-09-10 04:24:17 JST | leftover-reconstitute-0554a | completed | worker-1 | 14807 -c /dev/null vs pytest.ini+native and setup.cfg+native: test_default all (displaces both); -c /dev/null -o python_files=only_native.py vs native: only_native all; HOLD no View |
| 2026-09-10 04:24:17 JST | leftover-reconstitute-0557a | started | worker-1 | 14807 -c /dev/null vs pytest.ini+tox leftover; HOLD not PASS |
| 2026-09-10 04:24:52 JST | leftover-reconstitute-0557a | completed | worker-1 | 14807 -c /dev/null vs pytest.ini+tox and tox+native: test_default all; -c /dev/null -o python_files=only_tox.py vs tox.ini: only_tox all; HOLD no View |
| 2026-09-10 04:24:52 JST | leftover-reconstitute-0560a | started | worker-1 | 14807 -c /dev/null vs pytest.ini+setup.cfg leftover; HOLD not PASS |
| 2026-09-10 04:25:56 JST | leftover-reconstitute-0560a | completed | worker-1 | 14807 -c /dev/null vs pytest.ini+setup.cfg and tox+setup.cfg: test_default all; PYTEST_ADDOPTS=-c /dev/null vs pytest.ini+native: test_default all; HOLD no View |
| 2026-09-10 04:25:56 JST | leftover-reconstitute-0563a | started | worker-1 | 14807 --strict-config -c /dev/null vs dual cwd leftover; HOLD not PASS |
| 2026-09-10 04:31:38 JST | leftover-reconstitute-0563a | completed | worker-1 | 14807 --strict-config -c /dev/null vs dual cwd (ini+toml, toml+native, toml+tox, scfg+native, ini+iniopt, scfg+iniopt): test_default all; -c /dev/null vs pytest.ini+pyproject both tables: test_default all (displaces pytest9 UsageError); --strict-config -c /dev/null -o python_files=only_native.py vs pyboth: only_native all; HOLD no View |
| 2026-09-10 04:32:18 JST | leftover-reconstitute-0563a | completed | worker-1 | 14807 --strict-config -c /dev/null vs pytest.ini+native: test_default all; PYTEST_ADDOPTS=-c /dev/null vs tox.ini: test_default all; -c /dev/null -o python_files=only_cfg.py vs setup.cfg [tool:pytest]: only_cfg all; HOLD no View |
| 2026-09-10 04:32:18 JST | leftover-reconstitute-0566a | started | worker-1 | next unused leftover reconstitution after leftover-0563; 3062/14807-pytest.cfg/14608c complementary; HOLD not PASS |
| 2026-09-10 04:33:20 JST | leftover-reconstitute-0566a | completed | worker-1 | 3062 cfg-log -c /dev/null -s --log-cli-level=WARNING still default live-log (displaces setup.cfg format; rootdir /dev); 14807 pytest.cfg+pytest.ini -c /dev/null test_default; 14608c alt_lo_base -c /dev/null --db-url still 9.1.0 unrecognized (inifile /dev/null rootdir /dev); HOLD no View |
| 2026-09-10 04:33:20 JST | leftover-reconstitute-0569a | started | worker-1 | next unused leftover reconstitution after leftover-0566; 3062 ini / 14807 pytest.cfg+native / 14608c alt_inside; HOLD not PASS |
| 2026-09-10 04:33:58 JST | leftover-reconstitute-0569a | completed | worker-1 | 3062 ini -c /dev/null -s -o log_cli=true --log-cli-level=WARNING: 1 pass NO live-log (unlike leftover-0566 cfg-log default live-log); 14807 pytest.cfg+native -c /dev/null test_default; 14608c alt_inside -c /dev/null --db-url still 9.1.0 unrecognized inifile /dev/null rootdir /dev; HOLD no View |
| 2026-09-10 04:33:58 JST | leftover-reconstitute-0572a | started | worker-1 | next unused leftover reconstitution after leftover-0569; 3062 -s vs --log-cli-level split after /dev/null; HOLD not PASS |
| 2026-09-10 04:34:38 JST | leftover-reconstitute-0572a | completed | worker-1 | 3062 cfg-log -s -c /dev/null without --log-cli-level: 1 pass NO live-log (displacing log_cli=true stops live-log); --log-cli-level=WARNING without -s: default live-log; 14807 pytest.cfg+setup.cfg -c /dev/null test_default; HOLD no View |
| 2026-09-10 04:34:38 JST | leftover-reconstitute-0575a | started | worker-1 | next unused leftover reconstitution after leftover-0572; 3062 ini/toml --log-cli-level after /dev/null; HOLD not PASS |
| 2026-09-10 04:36:12 JST | leftover-reconstitute-0575a | completed | worker-1 | 3062 ini/toml -c /dev/null --log-cli-level=WARNING: 1 pass NO live-log (unlike leftover-0572 setup.cfg tree default live-log); 14807 pytest.cfg+tox.ini -c /dev/null test_default; HOLD no View |
| 2026-09-10 04:36:12 JST | leftover-reconstitute-0578a | started | worker-1 | next unused leftover reconstitution after leftover-0575; 3062 cfg-getini/ini -s / 14807 pytest.cfg+toml; HOLD not PASS |
| 2026-09-10 04:37:37 JST | leftover-reconstitute-0578a | completed | worker-1 | 3062 cfg-getini -c /dev/null --log-cli-level=WARNING: 1 pass NO live-log (unlike leftover-0572 cfg-log); ini -s -c /dev/null --log-cli-level still NO live-log; 14807 pytest.cfg+named toml -c /dev/null test_default; HOLD no View |
| 2026-09-10 04:37:37 JST | leftover-reconstitute-0581a | started | worker-1 | next unused leftover reconstitution after leftover-0578; 3062 tox/cfg --log-cli-level after /dev/null; HOLD not PASS |
| 2026-09-10 04:38:41 JST | leftover-reconstitute-0581a | completed | worker-1 | 3062 tox/cfg -c /dev/null --log-cli-level=WARNING: 1 pass NO live-log (cfg-log leftover-0572 live-log is not all setup.cfg trees); 14807 pytest.cfg+ini_options -c /dev/null test_default; HOLD no View |
| 2026-09-10 04:38:41 JST | leftover-reconstitute-0584a | started | worker-1 | next unused leftover reconstitution after leftover-0581; confirm cfg-log /dev/null live-log; HOLD not PASS |
| 2026-09-10 04:39:27 JST | leftover-reconstitute-0584a | completed | worker-1 | 3062 cfg-log -c /dev/null and --config-file=/dev/null --log-cli-level=WARNING: default live-log all (reproduces leftover-0572); 14807 pytest.cfg+pytest.ini --config-file=/dev/null test_default; HOLD no View |
| 2026-09-10 04:39:27 JST | leftover-reconstitute-0587a | started | worker-1 | next unused leftover reconstitution after leftover-0584; isolated setup.cfg / cache-clear / 14608c --config-file=/dev/null; HOLD not PASS |
| 2026-09-10 04:41:12 JST | leftover-reconstitute-0587a | completed | worker-1 | 3062 isolated fresh setup.cfg [tool:pytest] log_cli=true -c /dev/null --log-cli-level=WARNING: default live-log all; cfg-log --cache-clear still default live-log; 14608c --config-file=/dev/null --db-url still 9.1.0 unrecognized inifile /dev/null rootdir /dev; HOLD no View |
| 2026-09-10 04:41:12 JST | leftover-reconstitute-0590a | started | worker-1 | next unused leftover reconstitution after leftover-0587; pytest.ini/pyproject isolated with logging.warning; HOLD not PASS |
| 2026-09-10 04:41:42 JST | leftover-reconstitute-0590a | completed | worker-1 | 3062 isolated pytest.ini/pyproject with logging.warning: -s --log-cli-level=WARNING prints setup.cfg-format live-log all (leftover-0362 no-live-log was assert-True-only tests); -c /dev/null --log-cli-level default live-log; HOLD no View |
| 2026-09-10 04:41:42 JST | leftover-reconstitute-0593a | started | worker-1 | next unused leftover reconstitution after leftover-0590; tox.ini logging.warning / pyproject /dev/null / pytest.ini --log-file; HOLD not PASS |
| 2026-09-10 04:42:20 JST | leftover-reconstitute-0593a | completed | worker-1 | 3062 isolated pyproject -c /dev/null --log-cli-level default live-log; tox.ini [pytest] with logging.warning prints setup.cfg-format live-log; pytest.ini --log-file writes test_log.py:3 hdd3062WARNINGhello-log (leftover-0383 empty log was assert-True-only tests); HOLD no View |
| 2026-09-10 04:42:20 JST | leftover-reconstitute-0596a | started | worker-1 | next unused leftover reconstitution after leftover-0593; pytest.ini -s alone / pyproject+tox --log-file; HOLD not PASS |
| 2026-09-10 04:42:53 JST | leftover-reconstitute-0596a | completed | worker-1 | 3062 isolated pytest.ini log_cli=true -s alone prints live-log; pyproject and tox.ini --log-file write test_log.py:3 hdd3062WARNINGhello-log; HOLD no View |
| 2026-09-10 04:42:53 JST | leftover-reconstitute-0599a | started | worker-1 | next unused leftover reconstitution after leftover-0596; pyproject -s alone / pytest.ini without -s; HOLD not PASS |
| 2026-09-10 04:43:28 JST | leftover-reconstitute-0599a | completed | worker-1 | 3062 isolated pyproject -s alone live-log; pytest.ini log_cli=true without -s still live-log; --log-cli-level without -s still live-log; HOLD no View |
| 2026-09-10 04:43:28 JST | leftover-reconstitute-0602a | started | worker-1 | next unused leftover reconstitution after leftover-0599; pyproject/tox without -s / pytest.ini -c /dev/null no --log-cli-level; HOLD not PASS |
| 2026-09-10 04:44:00 JST | leftover-reconstitute-0602a | completed | worker-1 | 3062 isolated pyproject/tox.ini log_cli=true without -s still live-log; pytest.ini -c /dev/null without --log-cli-level NO live-log (displaces log_cli=true); HOLD no View |
| 2026-09-10 04:44:00 JST | leftover-reconstitute-0605a | started | worker-1 | next unused leftover reconstitution after leftover-0602; pyproject/tox -c /dev/null no level / pytest.ini --log-file no level; HOLD not PASS |
| 2026-09-10 04:44:43 JST | leftover-reconstitute-0605a | completed | worker-1 | 3062 isolated pyproject/tox.ini -c /dev/null without --log-cli-level NO live-log; pytest.ini --log-file without --log-file-level still writes live-log line; HOLD no View |
| 2026-09-10 04:44:43 JST | leftover-reconstitute-0608a | started | worker-1 | next unused leftover reconstitution after leftover-0605; pytest.ini /dev/null --log-file / pyproject+tox --log-file no level; HOLD not PASS |
| 2026-09-10 04:45:35 JST | leftover-reconstitute-0608a | completed | worker-1 | 3062 isolated pytest.ini -c /dev/null --log-file --log-file-level=WARNING writes default format WARNING hdd3062:test_log.py:3 hello-log NO live-log; pyproject/tox --log-file without level still writes pytest.ini-format line; HOLD no View |
| 2026-09-10 04:45:35 JST | leftover-reconstitute-0611a | started | worker-1 | next unused leftover reconstitution after leftover-0608; pyproject/tox /dev/null --log-file; HOLD not PASS |
| 2026-09-10 04:46:08 JST | leftover-reconstitute-0611a | completed | worker-1 | 3062 isolated pyproject/tox -c /dev/null --log-file --log-file-level=WARNING writes default format NO live-log; pytest.ini -c /dev/null --log-file without --log-file-level still writes default format; HOLD no View |
| 2026-09-10 04:46:08 JST | leftover-reconstitute-0614a | started | worker-1 | next unused leftover reconstitution after leftover-0611; pytest.ini/pyproject --log-cli-format with logging.warning; HOLD not PASS |
| 2026-09-10 04:46:50 JST | leftover-reconstitute-0614a | completed | worker-1 | 3062 isolated pytest.ini/pyproject --log-cli-format=CLI:... overrides cwd format (CLI:test_log.py:3 hello-log); -c /dev/null --log-cli-format --log-cli-level same CLI format; leftover-0377 pytest.ini no-live-log was assert-True-only tests; HOLD no View |
| 2026-09-10 04:46:50 JST | leftover-reconstitute-0617a | started | worker-1 | next unused leftover reconstitution after leftover-0614; pytest.ini/pyproject --log-file-format; HOLD not PASS |
| 2026-09-10 04:47:26 JST | leftover-reconstitute-0617a | completed | worker-1 | 3062 isolated pytest.ini/pyproject --log-file-format=FILE:... writes FILE:test_log.py:3 hello-log; pyproject -c /dev/null --log-cli-format --log-cli-level CLI:test_log.py:3 hello-log; HOLD no View |
| 2026-09-10 04:47:26 JST | leftover-reconstitute-0620a | started | worker-1 | next unused leftover reconstitution after leftover-0617; tox.ini --log-cli-format/--log-file-format; HOLD not PASS |
| 2026-09-10 04:48:19 JST | leftover-reconstitute-0620a | completed | worker-1 | 3062 isolated tox.ini --log-cli-format CLI:test_log.py:3 hello-log; --log-file-format FILE:test_log.py:3 hello-log; -c /dev/null --log-cli-format --log-cli-level CLI: same; HOLD no View |
| 2026-09-10 04:48:19 JST | leftover-reconstitute-0623a | started | worker-1 | next unused leftover reconstitution after leftover-0620; pytest.ini/pyproject -o log_cli_format; HOLD not PASS |
| 2026-09-10 04:49:03 JST | leftover-reconstitute-0626a | started | worker-1 | 3062 /dev/null --log-file-format leftover; HOLD not PASS |
| 2026-09-10 04:49:03 JST | leftover-reconstitute-0626a | completed | worker-1 | 3062 iso pytest.ini -c /dev/null --log-file-format=FILE:%(message)s writes FILE:hello-log NO live-log (displaces cwd log_format); PYTEST_ADDOPTS/ --strict-config -c /dev/null --log-file --log-file-level=WARNING writes default WARNING hdd3062:test_log.py:3 hello-log NO live-log; cfg-log -c /dev/null --log-file same default WARNING (displaces setup.cfg compact format); setup.cfg iso-cnull-log --log-cli-format CLI:test_log.py:3 hello-log; HOLD no View |
| 2026-09-10 04:49:07 JST | leftover-reconstitute-0623a | completed | worker-1 | 3062 isolated pytest.ini/pyproject -o log_cli_format=OCLIFMT:... live-log OCLIFMT:test_log.py:3 hello-log; pytest.ini -o log_file_format=OFILE:... writes OFILE:test_log.py:3 hello-log; HOLD no View |
| 2026-09-10 04:49:07 JST | leftover-reconstitute-0626a | started | worker-1 | next unused leftover reconstitution after leftover-0623; tox.ini -o format / pytest.ini PYTEST_ADDOPTS log_cli_format; HOLD not PASS |
| 2026-09-10 04:49:55 JST | leftover-reconstitute-0626a | completed | worker-1 | 3062 isolated tox.ini -o log_cli_format OCLIFMT live-log / -o log_file_format OFILE file; pytest.ini PYTEST_ADDOPTS log_cli_format with spaces rc=4 file-not-found %(message)s (env splits on space); HOLD no View |
| 2026-09-10 04:49:55 JST | leftover-reconstitute-0629a | started | worker-1 | next unused leftover reconstitution after leftover-0626; PYTEST_ADDOPTS no-space format / asctime+date-format on pytest.ini/pyproject; HOLD not PASS |
| 2026-09-10 04:50:33 JST | leftover-reconstitute-0629a | completed | worker-1 | 3062 isolated pytest.ini PYTEST_ADDOPTS no-space log_cli_format ENV:test_log.py:3:hello-log; pytest.ini/pyproject asctime+--log-cli-date-format=%H:%M:%S prints HH:MM:SS test_log.py:3 hello-log; HOLD no View |
| 2026-09-10 04:50:33 JST | leftover-reconstitute-0632a | started | worker-1 | next unused leftover reconstitution after leftover-0629; --log-cli-date-format without asctime on pytest.ini/pyproject; HOLD not PASS |
| 2026-09-10 04:51:09 JST | leftover-reconstitute-0632a | completed | worker-1 | 3062 isolated pytest.ini/pyproject --log-cli-date-format without asctime: live-log still test_log.py:3 hdd3062WARNINGhello-log (no timestamp); --log-cli-format without asctime + date-format: test_log.py:3 hello-log no timestamp; HOLD no View |
| 2026-09-10 04:51:09 JST | leftover-reconstitute-0635a | started | worker-1 | next unused leftover reconstitution after leftover-0632; --log-file-date-format with/without asctime; HOLD not PASS |
| 2026-09-10 04:51:50 JST | leftover-reconstitute-0635a | completed | worker-1 | 3062 isolated pytest.ini/pyproject --log-file-format asctime + --log-file-date-format=%H:%M:%S writes HH:MM:SS test_log.py:3 hello-log; --log-file-date-format without asctime writes cwd format no timestamp; HOLD no View |
| 2026-09-10 04:51:50 JST | leftover-reconstitute-0638a | started | worker-1 | next unused leftover reconstitution after leftover-0635; -o log_file= empty / log_file_level / pyproject date-format without asctime; HOLD not PASS |
| 2026-09-10 04:52:26 JST | leftover-reconstitute-0638a | completed | worker-1 | 3062 isolated pytest.ini -o log_file= empty still live-log; -o log_file_level=WARNING still cwd live-log; pyproject --log-file-date-format without asctime cwd format no timestamp; HOLD no View |
| 2026-09-10 04:52:26 JST | leftover-reconstitute-0641a | started | worker-1 | next unused leftover reconstitution after leftover-0638; -o log_file=path / --log-cli-level=DEBUG; HOLD not PASS |
| 2026-09-10 04:53:17 JST | leftover-reconstitute-0641a | completed | worker-1 | 3062 isolated pytest.ini/pyproject -o log_file=path writes cwd format line; --log-cli-level=DEBUG still WARNING live-log (test emits WARNING); leftover-0467 empty log was assert-True-only tests; HOLD no View |
| 2026-09-10 04:53:17 JST | leftover-reconstitute-0644a | started | worker-1 | next unused leftover reconstitution after leftover-0641; --log-cli-level=ERROR vs INFO; HOLD not PASS |
| 2026-09-10 04:53:48 JST | leftover-reconstitute-0644a | completed | worker-1 | 3062 isolated pytest.ini/pyproject --log-cli-level=ERROR hides WARNING live-log; --log-cli-level=INFO still prints WARNING live-log; HOLD no View |
| 2026-09-10 04:53:48 JST | leftover-reconstitute-0647a | started | worker-1 | next unused leftover reconstitution after leftover-0644; --log-file-level=ERROR vs INFO; HOLD not PASS |
| 2026-09-10 04:54:25 JST | leftover-reconstitute-0647a | completed | worker-1 | 3062 isolated pytest.ini/pyproject --log-file-level=ERROR empty file (WARNING filtered); --log-file-level=INFO writes cwd format line; leftover-0383 empty pytest.ini log was assert-True-only tests; HOLD no View |
| 2026-09-10 04:54:25 JST | leftover-reconstitute-0650a | started | worker-1 | next unused leftover reconstitution after leftover-0647; -o log_cli_level=ERROR / --log-file-level=DEBUG; HOLD not PASS |
| 2026-09-10 04:54:58 JST | leftover-reconstitute-0650a | completed | worker-1 | 3062 isolated pytest.ini/pyproject -o log_cli_level=ERROR hides WARNING live-log; --log-file-level=DEBUG writes cwd format WARNING line; HOLD no View |
| 2026-09-10 04:54:58 JST | leftover-reconstitute-0653a | started | worker-1 | next unused leftover reconstitution after leftover-0650; tox.ini asctime/ERROR leftover; HOLD not PASS |
| 2026-09-10 04:56:04 JST | leftover-reconstitute-0653a | completed | worker-1 | 3062 isolated tox.ini asctime+--log-cli-date-format=%H:%M:%S prints HH:MM:SS test_log.py:3 hello-log; --log-cli-level=ERROR hides live-log; --log-file-level=ERROR empty file; HOLD no View |
| 2026-09-10 04:56:04 JST | leftover-reconstitute-0656a | started | worker-1 | next unused leftover reconstitution after leftover-0653; 14807 --strict-config -c /dev/null -o verbosity=2; HOLD not PASS |
| 2026-09-10 04:56:36 JST | leftover-reconstitute-0656a | completed | worker-1 | 14807 --strict-config -c /dev/null -o verbosity=2 vs pytest.ini/native/setup.cfg [pytest] Failed: 8.4.1 test_default rc=0 / pytest 9 collects test_default then rc=4 unknown verbosity (Failed displaced then unknown option); HOLD no View |
| 2026-09-10 04:56:36 JST | leftover-reconstitute-0659a | started | worker-1 | next unused leftover reconstitution after leftover-0656; --strict-config -c /dev/null verbosity vs tox/named toml/ignored table; HOLD not PASS |
| 2026-09-10 04:57:13 JST | leftover-reconstitute-0659a | completed | worker-1 | 14807 --strict-config -c /dev/null -o verbosity=2 vs tox.ini/named toml/ignored table: 8.4.1 test_default rc=0 / pytest 9 collects test_default then rc=4 unknown verbosity; HOLD no View |
| 2026-09-10 04:57:13 JST | leftover-reconstitute-0662a | started | worker-1 | next unused leftover reconstitution after leftover-0659; pytest.cfg / addopts=--strict-config after /dev/null verbosity; HOLD not PASS |
| 2026-09-10 04:57:55 JST | leftover-reconstitute-0662a | completed | worker-1 | 14807 --strict-config -c /dev/null -o verbosity=2 vs pytest.cfg/setup.cfg [tool:pytest]: 8.4.1 rc=0 / pytest 9 rc=4; leftover-0476 -o addopts=--strict-config -c /dev/null -o verbosity=2 vs pytest.ini: 8.4.1/9.0.1/9.0.3 rc=0 / 9.1.0+ rc=4 (weaker split survives /dev/null); HOLD no View |
| 2026-09-10 04:57:55 JST | leftover-reconstitute-0665a | started | worker-1 | next unused leftover reconstitution after leftover-0662; leftover-0476 addopts=--strict-config after /dev/null vs tox/named toml/Failed; HOLD not PASS |
| 2026-09-10 05:01:40 JST | leftover-reconstitute-0665a | completed | worker-1 | 14807 -o addopts=--strict-config -c /dev/null -o verbosity=2 vs tox.ini/named toml/Failed/native/ignored table: 8.4.1 test_default rc=0; 9.0.1/9.0.3 rc=0 warning unknown verbosity collects test_default; 9.1.0+ rc=4; Failed displaced (test_default); env PYTEST_ADDOPTS=-o addopts=--strict-config same split vs tox; HOLD no View |
| 2026-09-10 05:03:52 JST | leftover-reconstitute-0665a | completed | worker-1 | 14807 leftover-0476 -o addopts=--strict-config -c /dev/null -o verbosity=2 vs tox.ini/named toml/setup.cfg [pytest] Failed: 8.4.1/9.0.1/9.0.3 rc=0 / 9.1.0+ rc=4 (weaker split survives /dev/null after Failed displaced); HOLD no View |
| 2026-09-10 05:03:52 JST | leftover-reconstitute-0668a | started | worker-1 | next unused leftover reconstitution after leftover-0665; --strict-config -c /dev/null -o minversion=99; HOLD not PASS |
| 2026-09-10 05:04:44 JST | leftover-reconstitute-0668a | completed | worker-1 | 14807 --strict-config -c /dev/null -o minversion=99 vs pytest.ini/native/setup.cfg [pytest] Failed: 8.4.1 test_default (minversion not enforced); pytest 9 rc=4 citing /dev/null:; HOLD no View |
| 2026-09-10 05:04:45 JST | leftover-reconstitute-0671a | started | worker-1 | next unused leftover reconstitution after leftover-0668; minversion=99 after /dev/null vs tox/named toml/ignored table; HOLD not PASS |
| 2026-09-10 05:20:13 JST | leftover-reconstitute-0671a | completed | worker-1 | 14807 --strict-config -c /dev/null -o minversion=99 vs tox.ini/named toml/ignored pytest.ini table: 8.4.1 test_default (minversion not enforced); pytest 9 rc=4 citing /dev/null:; HOLD no View |
| 2026-09-10 05:20:13 JST | leftover-reconstitute-0674a | started | worker-1 | next unused leftover reconstitution after leftover-0671; --strict-config -c /dev/null minversion=99 vs pytest.cfg/setup.cfg [tool:pytest]; minversion=9.1 after /dev/null; env/override-ini; HOLD not PASS |
| 2026-09-10 05:21:51 JST | leftover-reconstitute-0674a | completed | worker-1 | 14807 --strict-config -c /dev/null -o minversion=99 vs pytest.cfg/setup.cfg [tool:pytest]: 8.4.1 test_default / pytest 9 rc=4 citing /dev/null; minversion=9.1 after /dev/null vs tox/named/ignored/ini/native/Failed/pytest.cfg/setup.cfg: 8.4.1 test_default / 9.0.1-9.0.3 rc=4 citing /dev/null / 9.1.0+ test_default (leftover-0422 split survives /dev/null; Failed displaced); env minversion=99/9.1, --override-ini minversion=99, --config-file=/dev/null same as CLI; HOLD no View |
| 2026-09-10 05:22:26 JST | leftover-reconstitute-0677a | started | worker-1 | next unused leftover reconstitution after leftover-0674; --strict-config -c /dev/null -o minversion=9.1.1/9.0.2; addopts=--strict-config minversion=9.1/99 after /dev/null; HOLD not PASS |
| 2026-09-10 05:23:32 JST | leftover-reconstitute-0677a | completed | worker-1 | 14807 --strict-config -c /dev/null -o minversion=9.1.1 vs tox/named/Failed/pytest.cfg/ignored: 8.4.1 test_default / 9.0.1-9.1.0 rc=4 citing /dev/null / only 9.1.1 test_default; minversion=9.0.2 9.0.1-only rc=4 citing /dev/null; addopts=--strict-config minversion=9.1/99 same as CLI --strict-config (leftover-0476 weaker split does not apply to known minversion); Failed displaced; HOLD no View |
| 2026-09-10 05:31:37 JST | leftover-reconstitute-0680a | started | worker-1 | next unused leftover reconstitution after leftover-0677; leftover-0665 addopts verbosity after /dev/null vs pytest.ini/pytest.cfg/setup.cfg tool/dual cwd; minversion=8.0/9.0/9.0.1/9.1.0 after /dev/null; HOLD not PASS |
| 2026-09-10 05:32:43 JST | leftover-reconstitute-0680a | completed | worker-1 | 14807 leftover-0665 addopts=--strict-config -c /dev/null -o verbosity=2 vs pytest.ini/pytest.cfg/setup.cfg [tool:pytest]/dual cwd (ini+native/ini+toml/ini+pyboth): 8.4.1 test_default rc=0; 9.0.1/9.0.3 rc=0 warning collects test_default; 9.1.0+ rc=4; pyboth UsageError displaced; env vs named toml/ini/pytest.cfg same weaker split; minversion=8.0/9.0/9.0.1 after /dev/null all test_default including 8.4.1; minversion=9.1.0 same leftover-0422 split citing /dev/null; dual cwd minversion=9.1/99 same; Failed displaced; HOLD no View |
| 2026-09-10 05:32:43 JST | leftover-reconstitute-0683a | started | worker-1 | next unused leftover reconstitution after leftover-0680; leftover-0665 addopts verbosity vs more dual cwd; minversion=9.0.3 after /dev/null; HOLD not PASS |
| 2026-09-10 05:34:00 JST | leftover-reconstitute-0683a | completed | worker-1 | 14807 leftover-0665 addopts verbosity after /dev/null vs scfg+native/toml+native/ini+scfg/tox+native/toml+tox/scfg+toml: leftover-0476 weaker split (8.4.1 rc=0 / 9.0.x warning / 9.1.0+ rc=4) test_default; env vs Failed same weaker split Failed displaced; minversion=9.0.3 after /dev/null 8.4.1 test_default / 9.0.1 rc=4 citing /dev/null / 9.0.3+ test_default; dual cwd minversion=9.1 leftover-0422 split; HOLD no View |
| 2026-09-10 05:46:56 JST | leftover-reconstitute-0686a | started | worker-1 | next unused leftover reconstitution after leftover-0683; leftover-0665 remaining dual cwd iniopt; --config-file=/dev/null addopts verbosity; leftover-14101 xfail after /dev/null; HOLD not PASS |
| 2026-09-10 05:47:40 JST | leftover-reconstitute-0686a | completed | worker-1 | 14807 leftover-0665 addopts verbosity after /dev/null vs ini+iniopt/scfg+iniopt/toml+iniopt/tox+iniopt leftover-0476 weaker split test_default; --config-file=/dev/null same as -c; --override-ini verbosity=2 same weaker split; leftover-14101 --strict-config -c /dev/null -o xfail_strict=true 8.4.1 subtests missing / pytest 9 XPASS(strict) leftover-0470 survives /dev/null; leftover-3062 iso-log leftover-0476 weaker split; dual cwd iniopt minversion=9.1 leftover-0422 split; HOLD no View |
| 2026-09-10 05:47:40 JST | leftover-reconstitute-0689a | started | worker-1 | next unused leftover reconstitution after leftover-0686; leftover-0476 addopts=--strict-config vs known xfail_strict after /dev/null; HOLD not PASS |
| 2026-09-10 05:49:26 JST | leftover-reconstitute-0689a | completed | worker-1 | 14101 leftover-0476 addopts=--strict-config -c /dev/null -o xfail_strict=true same as CLI --strict-config: 8.4.1 subtests missing / pytest 9 all XPASS(strict) (weaker split does not apply to known xfail_strict); leftover-0476 verbosity execute 8.4.1 subtests missing / 9.0.x warning still runs (not strict) / 9.1.0+ rc=4 hides XPASS; CLI --strict-config verbosity pytest 9 all rc=4 hides XPASS; 14807 addopts xfail_strict collect test_default all Failed displaced; HOLD no View |
| 2026-09-10 05:52:14 JST | leftover-reconstitute-0692a | started | worker-1 | next unused leftover reconstitution after leftover-0689; 14608c leftover-0251 rescue vs -c /dev/null; HOLD not PASS |
| 2026-09-10 05:53:38 JST | leftover-reconstitute-0692a | completed | worker-1 | 14608c alt_inside --override-ini addopts=tests -c /dev/null/--config-file=/dev/null --db-url: 1 pass all including 9.1.0 (leftover-0251 rescue survives /dev/null); alt_lo_base same flags rc=5 all (addopts=tests loads tests/conftest so --db-url recognized, but test_it.py is outside tests/); HOLD no View |
| 2026-09-10 05:53:38 JST | leftover-reconstitute-0695a | started | worker-1 | next unused leftover reconstitution after leftover-0692; leftover-14608c leftover extras leftover-0566 /dev/null vs leftover-0251; HOLD not PASS |
| 2026-09-10 06:03:17 JST | leftover-reconstitute-0695a | completed | worker-1 | 14608c leftover-0251 --override-ini addopts=tests overwritten by -o addopts=--strict-config after /dev/null: 9.1.0 unrecognized --db-url (rescue lost); 9.1.1 leftover-0476 unknown verbosity; env PYTEST_ADDOPTS=-o addopts=tests -c /dev/null 1 pass including 9.1.0 (env survives /dev/null); ini addopts=tests displaced by /dev/null leftover-0566 split; CLI --strict-config verbosity pytest 9 all rc=4 hides rescue; alt_lo_base rescue+ /dev/null rc=5 all; HOLD no View |
| 2026-09-10 06:03:17 JST | leftover-reconstitute-0698a | started | worker-1 | next unused leftover reconstitution after leftover-0695; leftover-0251 vs leftover-0476 addopts last-wins after /dev/null; HOLD not PASS |
| 2026-09-10 06:03:49 JST | leftover-reconstitute-0698a | completed | worker-1 | 14608c leftover-0251 vs leftover-0476 addopts last-wins after /dev/null: later --override-ini addopts=tests or later -o addopts=tests rescues 9.1.0; later -o addopts=--strict-config loses rescue (9.1.0 unrecognized); -o addopts=tests -c /dev/null 1 pass including 9.1.0; leftover-0251 + -o verbosity=2 without --strict-config 1 pass all with pytest 9 warning; HOLD no View |
| 2026-09-10 06:06:27 JST | leftover-reconstitute-0701a | started | worker-1 | next unused leftover reconstitution after leftover-0698; leftover-13913 -c /dev/null vs no-path miss and tests/ rescue; HOLD not PASS |
| 2026-09-10 06:07:13 JST | leftover-reconstitute-0701a | completed | worker-1 | 13913 no-path -c /dev/null --db --write-idents: 8.4.1 rc=2 parent leftover dummy --db collisions after testpaths displaced; pytest 9 rc=4 unrecognized inifile /dev/null rootdir /dev; tests/ -c /dev/null and --config-file=/dev/null 1 pass all including 9.1.0 (rescue survives /dev/null); HOLD no View |
| 2026-09-10 06:07:13 JST | leftover-reconstitute-0704a | started | worker-1 | next unused leftover reconstitution after leftover-0701; leftover-13913 isolated no-path /dev/null leftover extras; HOLD not PASS |
| 2026-09-10 06:18:06 JST | leftover-reconstitute-0704a | completed | worker-1 | 13913 isolated no-path -c /dev/null --db --write-idents: 8.4.1 1 pass / pytest 9 rc=4 unrecognized (leftover-0701 8.4.1 rc=2 was leftover-dir --db collisions); tests/ -c /dev/null 1 pass all; leftover-0476 + tests/ 9.1.0+ rc=4 hides rescue; leftover-0251 --override-ini addopts=tests -c /dev/null 1 pass all; later -o addopts=--strict-config loses rescue pytest 9 unrecognized; later --override-ini addopts=tests wins; env addopts=tests 1 pass all; HOLD no View |
| 2026-09-10 06:18:06 JST | leftover-reconstitute-0707a | started | worker-1 | next unused leftover reconstitution after leftover-0704; leftover-13913 isolated leftover-0251 last-wins; HOLD not PASS |
| 2026-09-10 06:18:30 JST | leftover-reconstitute-0707a | completed | worker-1 | 13913 isolated leftover-0251 --override-ini addopts=tests -c /dev/null 1 pass all; later -o addopts=--strict-config 8.4.1 1 pass / pytest 9 unrecognized (rescue lost, no leftover-dir collisions); later --override-ini addopts=tests 1 pass all; env addopts=tests 1 pass all; tests/ + -o verbosity=2 without --strict-config 1 pass all with pytest 9 warning; -o addopts=tests -c /dev/null 1 pass all; HOLD no View |
| 2026-09-10 06:20:13 JST | leftover-reconstitute-0710a | started | worker-1 | next unused leftover reconstitution after leftover-0707; leftover-14048 -c /dev/null --pyargs; HOLD not PASS |
| 2026-09-10 06:20:44 JST | leftover-reconstitute-0710a | completed | worker-1 | 14048 PYTHONPATH=. -c /dev/null/--config-file=/dev/null --pyargs amodule.tests: 1 pass all (PYTHONPATH rescue survives /dev/null); no PYTHONPATH -c /dev/null --pyargs rc=4 missing __init__.py all; HOLD no View |
| 2026-09-10 06:20:44 JST | leftover-reconstitute-0713a | started | worker-1 | next unused leftover reconstitution after leftover-0710; leftover-14048 leftover extras leftover-0566 /dev/null --pyargs; HOLD not PASS |
| 2026-09-10 06:32:49 JST | leftover-reconstitute-0713a | completed | worker-1 | 14048 leftover-0476 + PYTHONPATH=. -c /dev/null --pyargs: leftover-0476 weaker split 8.4.1/9.0.x 1 pass / 9.1.0+ rc=4 hides PYTHONPATH rescue; CLI --strict-config verbosity pytest 9 all rc=4; leftover-0476 no PYTHONPATH 8.4.1/9.0.x missing __init__.py / 9.1.0+ unknown verbosity; -o/--override-ini pythonpath=. does not rescue --pyargs rc=4 all; leftover-0476 verbosity without --strict-config 1 pass all; leftover-14084 PYTHONPATH=. and subdir PYTHONPATH=.. survive /dev/null 1 pass all; subdir PYTHONPATH=. rc=4 all; HOLD no View |
| 2026-09-10 06:32:49 JST | leftover-reconstitute-0716a | started | worker-1 | next unused leftover reconstitution after leftover-0713; leftover-14084 leftover-0476 vs PYTHONPATH=..; HOLD not PASS |
| 2026-09-10 06:33:13 JST | leftover-reconstitute-0716a | completed | worker-1 | 14084 leftover-0476 + PYTHONPATH=. or subdir PYTHONPATH=.. -c /dev/null --pyargs leftover-0476 weaker split 8.4.1/9.0.x 1 pass / 9.1.0+ rc=4 hides rescue; CLI --strict-config verbosity pytest 9 all rc=4; leftover-0476 verbosity without --strict-config 1 pass all; leftover-14048 PYTHONPATH=. --pyargs amodule -c /dev/null 1 pass all; HOLD no View |
| 2026-09-10 06:35:46 JST | leftover-reconstitute-0719a | started | worker-1 | next unused leftover reconstitution after leftover-0716; leftover-11502 --cache-show -c /dev/null after normal run; HOLD not PASS |
| 2026-09-10 06:36:20 JST | leftover-reconstitute-0719a | completed | worker-1 | 11502 --cache-show -c /dev/null/--config-file=/dev/null after normal run: cachedir /dev/.pytest_cache cache is empty all (does not read project cache; leftover-0251 --cache-show after /dev/null run listed collapsed ::test_a); HOLD no View |
| 2026-09-10 06:36:20 JST | leftover-reconstitute-0722a | started | worker-1 | next unused leftover reconstitution after leftover-0719; leftover-11502 leftover extras leftover-0566 /dev/null --cache-show; HOLD not PASS |
| 2026-09-10 07:08:21 JST | leftover-reconstitute-0722a | completed | worker-1 | 11502 leftover-0476/--strict-config verbosity + leftover-0719 --cache-show -c /dev/null: cache empty rc=0 all including 9.1.0+ (leftover-0476 weaker split does not apply to --cache-show); leftover-0719 --cache-show without /dev/null after leftover-0719 precache lists tests/test_a.py::test_a; leftover-0719 --cache-clear -c /dev/null tests/test_a.py 1 pass with leftover-11502 cache warning; leftover-14148 leftover-0719 --cache-show -c /dev/null cache empty; leftover-14148 leftover-0719 -c /dev/null run 1 pass with cache warning; HOLD no View |
| 2026-09-10 07:08:21 JST | leftover-reconstitute-0725a | started | worker-1 | next unused leftover reconstitution after leftover-0722; leftover-14148 leftover-0476 vs leftover-0719 --cache-show / no:cacheprovider; HOLD not PASS |
| 2026-09-10 07:12:03 JST | leftover-reconstitute-0725a | completed | worker-1 | 14148 leftover-0476 + leftover-0719 --cache-show -c /dev/null cache empty rc=0 all (leftover-0476 does not apply to --cache-show); leftover-14148 -p no:cacheprovider leftover-0719 -c /dev/null AttributeError all (leftover-14148 miss survives /dev/null); leftover-0476 + leftover-14148 no:cacheprovider 8.4.1/9.0.x AttributeError / 9.1.0+ leftover-0476 rc=4 hides AttributeError; leftover-11502 leftover-14148 no:cacheprovider leftover-0719 --cache-show unrecognized --cache-show all; leftover-11502 leftover-0719 --cache-show leftover-0371 analog leftover-0719 cache_dir leftover-0719 cache empty; HOLD no View |
| 2026-09-10 08:12:23 JST | day-end-save-0800 | started | coordinator | now>=08:00 JST 保全; day_end.py save; no new wide exploration; no leftover-0728; no new R1 |
| 2026-09-10 08:13:32 JST | day-end-save-0800 | completed | coordinator | day_end.py save complete; restore hashes identical; leftover-0728 not started; KEEP 0; HARD_STOP not yet; HOLD no View |
| 2026-09-10 08:15:11 JST | day-end-save-0814 | started | coordinator | now>=08:00 JST 保全 tick; day_end.py save; no leftover-0728; no new R1; HARD_STOP not yet |
| 2026-09-10 08:15:35 JST | day-end-save-0814 | completed | coordinator | day_end.py save re-run complete; restore hashes identical; leftover-0728 not started; KEEP 0; HARD_STOP not yet; HOLD no View |
| 2026-09-10 08:30:03 JST | day-end-save-0829 | started | coordinator | now>=08:00 JST 保全 tick; day_end.py save; no leftover-0728; no new R1; HARD_STOP not yet |
| 2026-09-10 08:30:13 JST | hard-stop-user-authorized | completed | coordinator | user authorized close at 2026-09-10 08:30:13 JST; live=0; HARD_STOP.md written; original 09:00 not extended; leftover-0728 not started; KEEP 0; 9/2 and lab-hdd PIDs not killed |
| 2026-09-10 08:30:29 JST | day-end-save-0829 | completed | coordinator | day_end.py save re-run complete; restore hashes identical; leftover-0728 not started; KEEP 0; HARD_STOP not yet; HOLD no View |
