KNOWN FIX (sealed): earthly/earthly PR 3810 squash 892a4e03040feca16423d703a2a7ff0a380052cd.

failing_ref is squash parent 6b297d587cc12bea0372ca333fef34b522388b34.

handleCache expanded CACHE directory and mode but omitted expandArgs on opts.ID. converter.Cache used that literal as cacheID when GlobalCache was on, so leftover previous ARG value's mount was reused.

PR repair: if opts.ID != "", opts.ID, err = i.expandArgs(ctx, opts.ID, false, false) before converter.Cache. Test test-id-expand-args writes with --ID_1=test then hits with --id $ID_2 expanded to test.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
