KNOWN FIX (sealed): compose-spec/compose-go PR 654 squash 6adefd584b8088e0c6817bf54f5715595dd41301.

failing_ref is parent 65600cee45d45771a1faa6ddaf87b23ca4d2400c.

resolve dropped listed-without-equals names when user env had no match. Environment listing `FOO` then omitted FOO from the service map. Leftover identity was the image ENV default.

PR repair: resolve(a, fn, keepEmpty bool); environment keepEmpty=true keeps listed-without-equals as nil / bare name so the container unsets. Build args stay keepEmpty=false.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
